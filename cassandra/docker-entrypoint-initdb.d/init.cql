create keyspace if not exists sf WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor': 1 };

CREATE TABLE if not exists sf.overall (
    year int,
    district text,
    incidentId bigint,
    subid bigint,
    address text,
    category text,
    dayoftheweek text,
    description text,
    location text,
    resolution text,
    time timestamp,
    month int,
    day int,
    hour int,
    x text,
    y text,
    PRIMARY KEY ((year), time, incidentId, subid)
) WITH CLUSTERING ORDER BY (time DESC, incidentId DESC, subid DESC);

CREATE INDEX overall_index_incidentid ON sf.overall (incidentId);
CREATE INDEX overall_index_subid ON sf.overall (subid);


/* by district */
CREATE TABLE if not exists sf.bydistrict (
    year int,
    district text,
    incidentId bigint,
    subid bigint,
    address text,
    category text,
    dayoftheweek text,
    description text,
    location text,
    resolution text,
    time timestamp,
    month int,
    day int,
    hour int,
    x text,
    y text,
    PRIMARY KEY ((year,district), time, month, day, hour)
) WITH CLUSTERING ORDER BY (time DESC, month DESC, day DESC,hour DESC);
CREATE INDEX bydistrict_index_year ON sf.bydistrict (year);


/* by district/category */

CREATE TABLE if not exists sf.byCategories (
    year int,
    district text,
    category text,
    incidentId bigint,
    subid bigint,
    address text,
    dayoftheweek text,
    description text,
    location text,
    resolution text,
    time timestamp,
    month int,
    day int,
    hour int,
    x text,
    y text,
    PRIMARY KEY ((year,district,category), time, month, day, hour)
) WITH CLUSTERING ORDER BY (time DESC, month DESC, day DESC,hour DESC);
CREATE INDEX byCategories_index_year ON sf.byCategories (year);


CREATE TABLE if not exists sf.bycategory (
    year int,
    category text,
    incidentId bigint,
    subid bigint,
    address text,
    district text,
    dayoftheweek text,
    description text,
    location text,
    resolution text,
    time timestamp,
    month int,
    day int,
    hour int,
    x text,
    y text,
    PRIMARY KEY ((year,category), time, month, day, hour)
) WITH CLUSTERING ORDER BY (time DESC, month DESC, day DESC,hour DESC);
CREATE INDEX bycategory_index_year ON sf.bycategory (year);

truncate sf.overall;
truncate sf.bydistrict;
truncate sf.byCategories;
truncate sf.bycategory;

COPY sf.overall(incidentId, category, description, dayoftheweek, time, day,year,month, hour, district, resolution, address,x,y,location, subid) 
FROM '/opt/datasets/incidents.all.csv' 
WITH DELIMITER=';' and HEADER=false and DATETIMEFORMAT='%Y-%m-%d %H:%M:%S' and CHUNKSIZE=20000;

COPY sf.overall (year, district, incidentId, subid, address, category, dayoftheweek, description, location, resolution, time, month, day, hour,x,y) 
TO 'tmp_incidents.csv';

/* Importing dataset from original table */
COPY sf.bydistrict(year, district, incidentId, subid, address, category, dayoftheweek, description, location, resolution, time, month, day, hour,x,y) 
FROM 'tmp_incidents.csv' WITH CHUNKSIZE=10000;

COPY sf.byCategories(year, district, incidentId, subid, address, category, dayoftheweek, description, location, resolution, time, month, day, hour,x,y) 
FROM 'tmp_incidents.csv'  WITH CHUNKSIZE=10000;

COPY sf.bydistrict(year, district, incidentId, subid, address, category, dayoftheweek, description, location, resolution, time, month, day, hour,x,y) 
FROM 'tmp_incidents.csv'   WITH CHUNKSIZE=10000;

COPY sf.bycategory(year, district, incidentId, subid, address, category, dayoftheweek, description, location, resolution, time, month, day, hour,x,y) 
FROM 'tmp_incidents.csv' WITH CHUNKSIZE=10000;

