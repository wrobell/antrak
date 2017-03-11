drop table if exists track;
create table track (
    trip varchar(30),
    name varchar(30),
    device varchar(10),
    start timestamp with time zone not null,
    "end" timestamp with time zone not null,
    primary key (trip, name, device),
    foreign key (device, start) references position(device, timestamp),
    foreign key (device, "end") references position(device, timestamp)
);


