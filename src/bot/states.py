"""
Bot states для FSM
"""

from aiogram.fsm.state import State, StatesGroup


class PhotoSessionStates(StatesGroup):
    waiting_for_photos = State()
    collecting_brief = State()
    package_selection = State()
    processing_photos = State()
    video_generation = State()
    post_processing = State()
    payment_pending = State()
    delivery_ready = State()
    completed = State() 