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

plot_data <- function(data, lab, smooth=F, ...) {
    yaxt = NULL
    if (all(is.na(data))) {
        data[,1][1] <- 0
        data[,1][nrow(data)] <- 0
        yaxt = 'n'
    }

    if (smooth)
        data[,1] = lowess(data[,1] ~ time(data))$y

    plot(
        data, type='p', pch='.',
        major.format='%H:%M',
        major.ticks='hours', minor.ticks=F,
        main=NULL,
        mgp=c(2, 0.75, 0),
        ...
    )
    if (!is.null(yaxt)) {
        text(mean(range(time(data))), 0, 'no data')
    }
}

plot_track <- function(data) {
    cols = names(data)
    data = xts(data[, cols], order.by=data$timestamp)

    tdata = data[1]
    title = sprintf(
        '%s: %s - %s',
        strftime(time(tdata)[1], '%Y-%m-%d'),
        tdata$trip,
        tdata$name
    )
    par(mar=rep(0, 4))
    plot.new()
    text(0.5, 0.5, title, cex=1.5, font=2)

    col = ifelse(c(0, diff(as.numeric(data$z))) > 0, 'green', 'black')

    par(mar=c(0, 4, 0.5, 2) + 0.1)
    plot_data(data[, 'speed'], ylab='Speed [km/h]', col=col, xaxt='n')
    par(mar=c(4, 4, 0.5, 2) + 0.1)
    plot_data(data[, 'z'], ylab='Altitude [m]', col=col, xlab='Time')
    data.frame()
}

QUERY = "
select t.start, t.trip, t.name, timestamp, st_z(location) as z, speed
from track t
    inner join position p on t.device = p.device
        and p.timestamp between t.start and t.end
where p.device = ?device and t.trip || ' ' || t.name ~* ?query
"

args = commandArgs(trailingOnly=TRUE)

if (length(args) == 2)
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
par(mar=c(2, 4, 4, 2) + 0.1)
layout(matrix(c(1, 2, 3), ncol=1), heights=c(.06, .47, .47))
n = group_by(data, start, trip, name) %>% do(plot_track(.))
dev.off()

# vim: sw=4:et:ai
