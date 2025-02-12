from .new_compare import new_compare
from .page import page
from .save_score import save_score
from .sync import sync
from .upload import upload
from .view_final_order import view_final_order

root_handler = [page, new_compare, view_final_order, upload, sync, save_score]
