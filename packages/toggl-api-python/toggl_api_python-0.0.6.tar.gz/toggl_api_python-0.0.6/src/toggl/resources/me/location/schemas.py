from ...._schemas import ApiDataModel


class GetLocationResponse(ApiDataModel):
    city: str
    city_lat_long: str
    country_code: str
    country_name: str
    state: str

