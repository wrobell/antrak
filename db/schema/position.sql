drop table if exists position cascade;
create table position (
    device varchar(10),
    timestamp timestamp with time zone,
    heading float not null, -- true, degrees
    speed float not null,  -- km/h
    primary key (device, timestamp)
);

select AddGeometryColumn('position', 'location', 4326, 'POINT', 3);

