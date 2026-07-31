import logging

def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.WARNING)

    # clear out any handlers a library (e.g. firebase_admin/grpc) may have added
    root.handlers.clear()

    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)

    # file_handler = logging.FileHandler("pawplan.log", mode="a")
    # file_handler.setFormatter(formatter)
    # root.addHandler(file_handler)

    # your app's own namespace stays verbose
    logging.getLogger("pawplan").setLevel(logging.DEBUG)