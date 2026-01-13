from datetime import UTC, datetime
from pathlib import Path
from binance_data_loader import (
    BinanceDataDownloader,
    BinanceDataLoader,
    load_kline_data,
    get_date_range,
)

downloader = BinanceDataDownloader(
    prefix="data/futures/um/daily/klines/BTCUSDT/1h/",
    destination_dir=Path("./data"),
    output_format="parquet",
    start_date=datetime(2024, 1, 1, tzinfo=UTC),
    end_date=datetime(2024, 1, 31, tzinfo=UTC),
    keep_zip=True,
    max_workers=10,
    max_processors=4,
)

download_results, process_results = downloader.download()
