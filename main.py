import numpy as np
import pandas as pd
import folium
import geopandas as gpd
import pandas as pd
import numpy as np
from branca.colormap import linear
import folium
from folium.plugins import TimeSliderChoropleth
import datetime as dt
from bs4 import BeautifulSoup


if __name__ == '__main__':

    input_filename = 'street_sweeping.csv'
    output_filename = 'street_sweeping.html'

    df = pd.read_csv(input_filename)
    df = df.rename(columns={'the_geom': 'geometry'})
    df['featurecla'] = 'Land'
    df['scalerank'] = 1
    df['min_zoom'] = 1.0
    df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry'])
    gdf = gpd.GeoDataFrame(df, geometry='geometry')

    # Sweeping starts on April, 1st
    start_day = dt.datetime.strptime('APRIL 1', '%B %d').timetuple().tm_yday
    num_days = 365 - start_day + 1
    datetime_index = pd.date_range("2024-4-1", periods=num_days, freq="D")
    dt_index_epochs = datetime_index.astype("int64") // 10 ** 9
    dt_index = dt_index_epochs.astype("U10")
    months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']

    styledata = {}
    for zone in gdf.index:
        sweep = [False]*num_days
        for month in months:
            if month in gdf.iloc[zone]:
                for day in str(gdf.iloc[zone][month]).split(','):
                    if day.isnumeric():
                        day_of_year = dt.datetime.strptime(f'{month} {day}', '%B %d').timetuple().tm_yday
                        day_from_start = day_of_year - start_day
                        sweep[day_from_start] = True
        zone_df = pd.DataFrame(
            {
                "color": "#631078",
                "opacity": 0.8*np.array(sweep)+0.2
            },
            index=dt_index,
        )
        styledata[zone] = zone_df


    styledict = {
        str(zone): data.to_dict(orient="index") for zone, data in styledata.items()
    }

    min_lat = gdf.bounds.miny.min()
    max_lat = gdf.bounds.maxy.max()
    min_lon = gdf.bounds.minx.min()
    max_lon = gdf.bounds.maxx.max()
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    m = folium.Map([center_lat, center_lon], zoom_start=10, width='100%', min_zoom=10)

    TimeSliderChoropleth(
        gdf.to_json(),
        styledict=styledict,
        init_timestamp=-num_days,
        overlay=True
    ).add_to(m)

    m.save(output_filename)
