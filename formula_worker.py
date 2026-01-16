'''
@Description: 
@Author: QiLan Gao
@Date: 2025-06-06 16:07:31
@LastEditTime: 2025-06-06 16:07:36
@LastEditors: QiLan Gao
'''
# formula_worker.py
from pix2text import Pix2Text
import concurrent.futures
import multiprocessing

class FormulaWorker:
    def __init__(self):
        self.p2t = Pix2Text.from_config()

        # 设置线程池，线程数 = 总核数 * 25%
        cpu_count = multiprocessing.cpu_count()
        thread_count = max(1, int(cpu_count * 0.25))
        print(f"[INFO] 初始化线程池，CPU核数={cpu_count}，线程池大小={thread_count}")

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=thread_count)

    def recognize(self, filepath):
        # 在线程池中提交任务
        future = self.executor.submit(self.p2t.recognize_formula, filepath)
        return future.result()  # 等待结果并返回
