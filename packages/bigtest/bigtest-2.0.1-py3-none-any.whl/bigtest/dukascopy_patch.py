import dukascopy_python as dp
from datetime import datetime
from time import sleep
import logging

# Get logger as used in the original module
logger = logging.getLogger("dukascopy_python")

def patched_stream(
    instrument,
    interval,
    offer_side,
    start,
    end=None,
    max_retries=7,
    limit=None,
    logger=None,
):
    if logger is None:
        logger = logging.getLogger("dukascopy_python")
    # Access _fetch from the module
    _fetch = dp._fetch
    INTERVAL_TICK = dp.INTERVAL_TICK

    cursor = int(start.timestamp() * 1000)
    end_timestamp = int(end.timestamp() * 1000) if end is not None else None
    
    no_of_retries = 0
    is_first_iteration = True

    while True:
        try:
            logger.debug(f"fetching {instrument} {interval} {offer_side} {cursor}")
            
            lastUpdates = _fetch(
                instrument=instrument,
                interval=interval,
                offer_side=offer_side,
                last_update=cursor,
                limit=limit,
            )
            
            logger.debug(f"Raw lastUpdates length: {len(lastUpdates) if lastUpdates else 0}")

            # PATCH: Filter out None rows immediately
            if lastUpdates:
                lastUpdates = [row for row in lastUpdates if row is not None]

            if not is_first_iteration and lastUpdates and lastUpdates[0][0] == cursor:
                lastUpdates = lastUpdates[1:]

            if len(lastUpdates) < 1:
                if end is not None:
                    break
                else:
                    continue

            for row in lastUpdates:
                # --- PATCH START ---
                if row is None: 
                    continue
                # --- PATCH END ---
                
                if end_timestamp is not None and row[0] > end_timestamp:
                    return
                if interval == INTERVAL_TICK:
                    row[-1] = row[-1] / 1_000_000
                    row[-2] = row[-2] / 1_000_000
                yield row
                cursor = row[0]

            logger.info(
                f"current timestamp :{datetime.fromtimestamp(cursor/1000).isoformat()}"
            )

            no_of_retries = 0
            is_first_iteration = False

        except Exception as e:
            import traceback
            stacktrace = traceback.format_exc()
            no_of_retries += 1
            if max_retries is not None and (no_of_retries - 1) > max_retries:
                logger.debug("error fetching")
                logger.debug(f"{e}\n{stacktrace}")
                raise e
            else:
                logger.debug(f"an error occured {e}")
                logger.debug(f"{e}\n{stacktrace}")
                logger.debug("retrying")
                sleep(1)
            continue

def apply_patch():
    print("[DukascopyPatch] Applying monkey patch to _stream...")
    dp._stream = patched_stream
    print("[DukascopyPatch] Patch applied.")
