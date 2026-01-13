from datetime import datetime

from phable import GridBuilder, Number

grid = (
    GridBuilder()
    .set_meta({"dis": "Temperature Data"})
    .add_col("ts")
    .add_col("val", meta={"unit": "°F"})
    .add_row({"ts": datetime.now(), "val": Number(72.5, "°F")})
    .add_row({"ts": datetime.now(), "val": Number(73.1, "°F")})
    .build()
)

for col in grid.cols:
    print(col.name, col.meta)
