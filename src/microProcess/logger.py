from constants import *


class Logger:
    @staticmethod
    def log_make_message(method):
        def make_message(self, id_, comp, arg):
            res = method(self, id_, comp, arg)
            if NEC < self.log_level:
                print(f'information: {self} > Preparing message: {ORDERS[id_]}({id_}), {comp}, {arg}')
            return res
        return make_message

    @staticmethod
    def log_send(method):
        def send(self, mess):
            if N_NEC < self.log_level:
                print(f'information: {self} > Sending to pico: 0x{mess.hex()}')
            method(self, mess)
        return send

    @staticmethod
    def log_receive(method):
        def receive(self):
            res = method(self)
            if N_NEC < self.log_level:
                print(f'information: {self} > Received from pico: 0x{res.hex()}')
            return res
        return receive

    @staticmethod
    def log_pull(method):
        def pull(self, type_):
            if N_NEC < self.log_level:
                print(f'information: {self} > Pulling {CATEGORIES[type_]}({type_}) from main')
            method(self, type_)
        return pull

    @staticmethod
    def log_next(method):
        def next_(self, type_):
            if N_NEC < self.log_level:
                print(f'information: {self} > Getting next {CATEGORIES[type_]}({type_}) order')
            method(self, type_)
        return next_

    @staticmethod
    def log_manage_feedback(method):
        def manage_feedbak(self, id_, order_id):
            if NEC < self.log_level:
                print(f'information: {self} > Processing feedback: {FEEDBACKS[id_]}({id_}), {ORDERS[order_id]}({order_id})')
            method(self, id_, order_id)
        return manage_feedbak
