import time
import model
import traceback

from rpa.utils import controller
from sqlalchemy import text

control = controller.Controller(model.Queue)
control.clear_status()

# Limpa os registros
sql = text(f'''
    UPDATE public."desenvolvimento" 
    SET results_status = 'Pendente'
''')
control.session.execute(sql)
control.session.commit()


counter = 0
try:
    while True:
        control.yield_command()
        queue,queue_files = control.get_next_queue()
        if queue is None:
            break
        else:
            try:
                counter += 1
                control.logger.info(f'Processando registro: {queue}')
                # control.logger.error('erro')
                # control.logger.debug('debug')
                # control.logger.warning('warn')
                if counter == 1:
                    control.get_input(
                        title='titulo',
                        question='question'
                        # image: BytesIO | None = None,
                        # options: list[str] | None = None,
                    )
                if counter % 3 == 0:
                    raise Exception('Testando')
                time.sleep(1)
                queue.results_json = {'testando':'ok'}
                queue.results_status = 'Concluído'
                print(1)
            except Exception as e:
                queue.results_json = {'testando':'falha'}
                queue.results_status = 'Erro'
                queue.results_error = str(e)
                queue.results_stacktrace = str(traceback.format_exc())
                control.logger.error(str(e))
            finally:
                control.session.commit()
except KeyboardInterrupt as e:
    control.logger.info('Parando...')
except Exception as e:
    control.logger.error(str(e))

control.clear_status()
control.session.close()