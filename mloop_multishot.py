import lyse
import numpy as np
import os
import config_get


def lorentzian(x, s=0.05):
    return 1 / (1 + x ** 2) + s * np.random.randn()


def cost_analysis(key_path=[], ignore_nans=False, x=None):
    # Retrieve current lyse DataFrame
    df = lyse.data()

    # Retrieve most recent parameter of interest
    if len(df) and tuple(key_path) in df:
        rec_param = df[tuple(key_path)].iloc[-1]
        shot_file = os.path.split(df['filepath'].iloc[-1])[-1]
    # If it doesn't exist, use the latest M-LOOP parameter value
    elif x is None:
        rec_param = 1.2
        shot_file = '<fake_shot>'
    else:
        rec_param = lorentzian(x)
        shot_file = '<fake_data>'

    if ignore_nans and np.isnan(rec_param):
        return None
    else:
        # Return cost function such that result is maximised
        print('Returning cost_analysis based on {:}'.format(shot_file))
        return -1.0 * rec_param


if __name__ == '__main__':
    # Runs each time this analysis routine does
    mloop_config = config_get.cfgget()
    if not hasattr(lyse.routine_storage, "queue"):
        print("First execution of lyse routine...")
        import Queue
        lyse.routine_storage.queue = Queue.Queue()
    if (
        hasattr(lyse.routine_storage, "optimisation")
        and lyse.routine_storage.optimisation.is_alive()
    ):
        lyse.routine_storage.queue.put(
            cost_analysis(
                key_path=mloop_config['opt_param'],
                ignore_nans=mloop_config['ignore_nans'],
                x=lyse.routine_storage.x if mloop_config['mock'] else None
            )
        )
    else:
        print("(Re)starting optimisation process...")
        import threading
        from mloop_interface import optimus
        lyse.routine_storage.optimisation = threading.Thread(target=optimus)
        lyse.routine_storage.optimisation.daemon = True
        lyse.routine_storage.optimisation.start()