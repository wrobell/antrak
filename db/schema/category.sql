drop table if exists category;
create table category (
    mode varchar(10),
    device varchar(10),
    start timestamp,
    "end" timestamp,
    category varchar(10),
    rank integer not null,
    primary key (mode, device, start, category),
    foreign key (device, start) references position(device, timestamp),
    foreign key (device, "end") references position(device, timestamp)
);


