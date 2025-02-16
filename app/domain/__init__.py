from .new_compare import new_compare
from .page import page
from .save_score import save_score
from .sync import sync
from .upload import upload
from .view_final_order import view_final_order
from .get_operators_1v1_matrix import get_operators_1v1_matrix

root_handler = [page, new_compare, view_final_order, upload, sync, save_score, get_operators_1v1_matrix]
