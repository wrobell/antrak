drop table if exists position cascade;
create table position (
    device varchar(10),
    timestamp timestamp,
    heading float,
    speed float,
    primary key (device, timestamp)
);

select AddGeometryColumn('position', 'location', 4326, 'POINT', 3);

