import os
import random

import psychopy  # Necessary for paths to custom modules to load

import eyelinker

import changedetection
import visualsearch


data_directory = os.path.join(
    os.path.expanduser('~'), 'Desktop', 'Colin', 'VSCD', 'Data')

tl_stim_path = os.path.join(
    os.path.expanduser('~'), 'Desktop', 'Colin', 'VSCD', 'stim')

stim_time = 2

cd_instructs = [
    ('Welcome to the experiment. Press space to continue.'),
    ('In this experiment you will be remembering colors.\n\n'
     '6 squares with different colors will appear. '
     'Remember as many colors as you can.\n\n'
     'After a short delay, a square will reappear.\n\n'
     'If it has the SAME color, press the "S" key. '
     'If it has a DIFFERENT color, press the "D" key.\n'
     'If you are not sure, just take your best guess.\n\n'
     'You will get breaks in between blocks.\n\n'
     'Press space to continue.'),
]

cd_task = changedetection.Ktask(
        tracker=None,
        experiment_name='VSCD_K',
        data_fields=changedetection.data_fields,
        monitor_distance=90,
        data_directory=data_directory,
        instruct_text=cd_instructs,
        max_per_quad=2,
        number_of_blocks=5,
        number_of_trials_per_block=80,
        sample_time=stim_time,
        repeat_stim_colors=False,
        repeat_test_colors=True,
    )

tl_task = visualsearch.TLTask(
        tracker=None,
        experiment_name='VSCD_TL',
        data_fields=visualsearch.data_fields,
        monitor_distance=90,
        data_directory=data_directory,
        iti_time=2,
        max_per_quad=2,
        number_of_blocks=5,
        number_of_trials_per_block=80,
        response_time_limit=stim_time,
        set_sizes=[6],
        stim_path=tl_stim_path,
)


# Hooks
def setup_tracker(self):
    self.tracker = eyelinker.EyeLinker(
        self.experiment_window,
        self.experiment_name.split('_')[1] + self.experiment_info['Subject Number'] + '.edf',
        'BOTH')

    self.tracker.initialize_graphics()
    self.tracker.open_edf()
    self.tracker.initialize_tracker()
    self.tracker.send_tracking_settings()


def show_eyetracking_instructions(self):
    self.tracker.display_eyetracking_instructions()
    self.tracker.setup_tracker()


def pretrial_setup(self, _, block_num, trial_num):
    if trial_num % 5 == 0:
        self.tracker.drift_correct()

    status = 'Block {}, Trial {}'.format(block_num, trial_num)
    self.tracker.send_status(status)

    self.tracker.send_message('BLOCK %d' % block_num)
    self.tracker.send_message('TRIAL %d' % trial_num)

    self.tracker.start_recording()


def end_trial(self, _):
    self.tracker.stop_recording()


def kill_tracker(self):
    self.tracker.set_offline_mode()
    self.tracker.close_edf()
    self.tracker.transfer_edf()
    self.tracker.close_connection()


tasks = [cd_task, tl_task]
random.shuffle(tasks)

for task in tasks:
    try:
        task.run(
            setup_hook=setup_tracker,
            before_first_trial_hook=show_eyetracking_instructions,
            pre_trial_hook=pretrial_setup,
            post_trial_hook=end_trial,
            end_experiment_hook=kill_tracker,
        )
    except Exception as e:
        kill_tracker(task)
        raise e
