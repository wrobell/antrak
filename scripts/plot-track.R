#!/usr/bin/Rscript
#
# AnTrak - Activity and location data analysis
#
# Copyright (C) 2017-2018 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


library(dplyr)
library(RPostgreSQL)
library(xts)

# set to 1h, so current rolling average shows how many kilometers travelled
SPEED_RM_WIDTH_MIN = 60
SPEED_RM_WIDTH_HOUR = SPEED_RM_WIDTH_MIN * SPEED_RM_WIDTH_MIN

QUERY = "
select
    start,
    trip,
    name,
    timestamp,
    z,
    speed,
    sum(st_distance(st_transform(p1, 3857), st_transform(p2, 3857))) over (order by timestamp) as distance
from (
    select
        t.start,
        t.trip,
        t.name,
        timestamp,
        st_z(location) as z,
        speed,
        location as p1,
        lag(location) over (order by timestamp) as p2
    from track t
        inner join position p on t.device = p.device
            and p.timestamp between t.start and t.end
    where p.device = ?device and t.trip || ' ' || t.name ~* ?query
) t
order by timestamp
"

track_plot <- function(track, ...) {
    data = track$data
    data.mean = track$data.mean
    data.dist = track$data.dist

    # TODO: show altitude change
    # col = ifelse(c(0, diff(data$z)) > 0, 'green', 'black')

    names(data) <- c('Speed', 'Altitude')
    p = plot(
        data[, c('Speed', 'Altitude')], type='p', pch='.',
        grid.ticks.on='minutes',
        format.labels='%H:%M',
        major.ticks='minutes',
        minor.ticks=F,
        multi.panel=T,
        yaxis.right=F,
        yaxis.same=F,
        col='black',
        main=track$title,
        ...
    )
    addSeries(data.mean, type='l', col='orange', on=1)
    addEventLines(data.dist, cex=1.1, adj=c(0, 1.5), srt=270, col='red', font=2)
    p
}

track_data <- function(data) {
    tdata = first(data)  # create title based on first row data
    title = sprintf(
        '%s: %s - %s',
        strftime(tdata$start, '%Y-%m-%d'),
        tdata$trip,
        tdata$name
    )

    cols = c('speed', 'z')

    # if no more than 2h of data, then rolling average using minutes
    # instead of hours
    mean_width = ifelse(
        length(data) <= SPEED_RM_WIDTH_HOUR * 2,
        SPEED_RM_WIDTH_MIN,
        SPEED_RM_WIDTH_HOUR
    )
    data.ts = xts(data[, cols], order.by=data$timestamp)
    data.mean = rollmean(data.ts[, 'speed'], mean_width)

    data$cat_distance = cut(data$distance, seq(0, max(data$distance, na.rm=T), 200))
    data.dist = aggregate(data, list(data$cat_distance), last)
    data.dist$distance = sprintf('%.0f m', data.dist$distance)
    data.dist = xts(data.dist[, 'distance'], order.by=data.dist$timestamp)

    list(
        title=title,
        data=data.ts,
        data.mean=data.mean,
        data.dist=data.dist
    )
}

args = commandArgs(trailingOnly=TRUE)

if (length(args) == 2) {
    query = args[1]
    output = args[2]
} else {
    cat('Usage:\n    plot-track.R [query] output\n', file=stderr())
    quit('no', 1)
}

drv = dbDriver('PostgreSQL')
conn = dbConnect(drv, dbname='antrak')
sql = sqlInterpolate(ANSI(), QUERY, device='default', query=query)
data = dbGetQuery(conn, sql)

pdf(output, width=10, height=10)
plots = (
    group_by(data, start, trip, name)
    %>% do(data=track_data(.))
    %>% do(data=track_plot(.$data))
    %>% do(data=print(.$data))
)
dev.off()

# vim: sw=4:et:ai
