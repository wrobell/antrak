#!/usr/bin/Rscript
#
# AnTrak - Activity and location data analysis
#
# Copyright (C) 2017 by Artur Wroblewski <wrobell@riseup.net>
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

ROLL_MEAN = 60 * 60

QUERY = "
select t.start, t.trip, t.name, timestamp, st_z(location) as z, speed
from track t
    inner join position p on t.device = p.device
        and p.timestamp between t.start and t.end
where p.device = ?device and t.trip || ' ' || t.name ~* ?query
"

plot_track <- function(data, ...) {
    track = data$data
    data = track$data
    data.mean = track$data.mean

    # TODO: show altitude change
    # col = ifelse(c(0, diff(data$z)) > 0, 'green', 'black')

    yaxt = NULL
    if (all(is.na(data))) {
        data[,1][1] <- 0
        data[,1][nrow(data)] <- 0
        yaxt = 'n'
    }

    names(data) <- c('Speed', 'Altitude')
    p = plot(
        data, type='p', pch='.',
        grid.ticks.on='hours',
        format.labels='%H:%M',
        major.ticks='hours', minor.ticks=F,
        multi.panel=T,
        yaxis.right=F,
        yaxis.same=F,
        col='black',
        main=track$title,
        ylab=c('a', 'b'),
        ...
    )
    addSeries(data.mean, type='l', col='orange', on=1)

    if (!is.null(yaxt)) {
        text(mean(range(time(data))), 0, 'no data')
    }
    p
}

track_data <- function(data) {
    tdata = data[1,]
    title = sprintf(
        '%s: %s - %s',
        strftime(tdata$start, '%Y-%m-%d'),
        tdata$trip,
        tdata$name
    )

    cols = c('speed', 'z')

    data = xts(data[, cols], order.by=data$timestamp)
    data.mean = rollmean(data[, 'speed'], ROLL_MEAN)
    list(
        title=title,
        data=data,
        data.mean=data.mean
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

pdf(output)
plots = (
    group_by(data, start, trip, name)
    %>% do(data=track_data(.))
    %>% do(data=plot_track(.))
    %>% select(data)
)

for (p in plots[[1]]) {
    print(p)
}
dev.off()

# vim: sw=4:et:ai
