from constants import *

log = print


class Logger:
    @staticmethod
    def log_make_message(method):
        def make_message(self, id_, comp, arg):
            res = method(self, id_, comp, arg)
            if NOT_NECESSARY <= self.log_level:
                log(f'{self} > Preparing message: {ORDERS[id_]}({id_}), {comp}, {arg}')
            return res
        return make_message

    @staticmethod
    def log_send(method):
        def send(self, mess):
            if NECESSARY <= self.log_level:
                log(f'{self} > Sending to pico: 0x{mess.hex()}')
            method(self, mess)
        return send

    @staticmethod
    def log_receive(method):
        def receive(self):
            res = method(self)
            if NECESSARY <= self.log_level:
                log(f'{self} > Received from pico: 0x{res.hex()}')
            return res
        return receive

    @staticmethod
    def log_manage_feedback(method):
        def manage_feedback(self, id_, order_id):
            if NOT_NECESSARY <= self.log_level:
                log(f'{self} > Processing feedback: {FEED_BACKS[id_]}({id_}), {ORDERS[order_id]}({order_id})')
            method(self, id_, order_id)
        return manage_feedback

    @staticmethod
    def log_pull(method):
        def pull(self, type_):
            if NECESSARY <= self.log_level:
                log(f'{self} > Pulling {CATEGORIES[type_]}({type_}) from main')
            method(self, type_)
        return pull
