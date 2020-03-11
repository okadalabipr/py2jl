import numpy as np
from scipy.integrate import ode

from .model.name2idx import parameters as C
from .model.name2idx import variables as V
from .model.differential_equation import diffeq
from .solver import get_steady_state, solveode


observables = [
    'Phosphorylated_ErbB1',
    'Phosphorylated_ErbB2',
    'Phosphorylated_ErbB3',
    'Phosphorylated_ErbB4',
    'Phosphorylated_Akt',
    'Phosphorylated_ERK',
    'Phosphorylated_cFos',
    'Phosphorylated_Shc',
]

class NumericalSimulation(object):

    tspan = [0,7200] # Unit time: 1 sec.
    t = np.arange(tspan[0],tspan[-1]+1)/60. # sec. -> min. (plot_func.py)

    conditions = ['EGF', 'HRG']

    simulations = np.empty((len(observables),len(t),len(conditions)))

    def simulate(self,x,y0):
        # get steady state
        y0[V.E] = 0.0
        y0[V.H] = 0.0
        (T0, Y0) = self._get_steady_state(diffeq,y0,self.tspan,tuple(x))
        if T0 < self.tspan[-1]:
            return False
        else:
            y0 = Y0[:]
        # add ligand
        copy_x = x[:]
        for i,condition in enumerate(self.conditions):
            if condition == 'EGF':
                y0[V.E] = 10.0
                y0[V.H] = 0.0
            elif condition == 'HRG':
                y0[V.E] = 0.0
                y0[V.H] = 10.0
            elif condition == 'EGF_U0126':
                y0[V.E] = 10.0
                y0[V.H] = 0.0
                x[C.V1] = copy_x[C.V1]*0.5
                x[C.V2] = copy_x[C.V2]*0.5
            elif condition == 'HRG_U0126':
                y0[V.E] = 0.0
                y0[V.H] = 10.0
                x[C.V1] = copy_x[C.V1]*0.5
                x[C.V2] = copy_x[C.V2]*0.5

            (T,Y) = self._solveode(diffeq,y0,self.tspan,tuple(x))

            if T[-1] < self.tspan[-1]:
                return False
            else:
                self.simulations[observables.index('Phosphorylated_ErbB1'),:,i] = (
                    2*Y[:,V.E11P] + Y[:,V.E12P] + Y[:,V.E13P] + Y[:,V.E14P] +
                    2*Y[:,V.E11G] + Y[:,V.E12G] + Y[:,V.E13G] + Y[:,V.E14G] +
                    2*Y[:,V.E11S] + Y[:,V.E12S] + Y[:,V.E13S] + Y[:,V.E14S] +
                                                + Y[:,V.E13I] + Y[:,V.E14I] +
                    2*Y[:,V.E11R] + Y[:,V.E12R] + Y[:,V.E13R] + Y[:,V.E14R] +
                    2*Y[:,V.E11T] + Y[:,V.E12T] + Y[:,V.E13T] + Y[:,V.E14T]
                )
                self.simulations[observables.index('Phosphorylated_ErbB2'),:,i] = (
                    Y[:,V.E12P] + Y[:,V.E23P] + Y[:,V.E24T] +
                    Y[:,V.E12G] + Y[:,V.E23G] + Y[:,V.E24G] +
                    Y[:,V.E12S] + Y[:,V.E23S] + Y[:,V.E24S] +
                                + Y[:,V.E23I] + Y[:,V.E24I] +
                    Y[:,V.E12R] + Y[:,V.E23R] + Y[:,V.E24R] +
                    Y[:,V.E12T] + Y[:,V.E23T] + Y[:,V.E24T]
                )
                self.simulations[observables.index('Phosphorylated_ErbB3'),:,i] = (
                    Y[:,V.E13P] + Y[:,V.E23P] + Y[:,V.E34P] +
                    Y[:,V.E13G] + Y[:,V.E23G] + Y[:,V.E34G] +
                    Y[:,V.E13S] + Y[:,V.E23S] + Y[:,V.E34S] +
                    Y[:,V.E13I] + Y[:,V.E23I] + Y[:,V.E34I] +
                    Y[:,V.E13R] + Y[:,V.E23R] + Y[:,V.E34R] +
                    Y[:,V.E13T] + Y[:,V.E23T] + Y[:,V.E34T]
                )
                self.simulations[observables.index('Phosphorylated_ErbB4'),:,i] = (
                    Y[:,V.E14P] + Y[:,V.E24P] + Y[:,V.E34P] + 2*Y[:,V.E44P] +
                    Y[:,V.E14G] + Y[:,V.E24G] + Y[:,V.E34G] + 2*Y[:,V.E44G] +
                    Y[:,V.E14S] + Y[:,V.E24S] + Y[:,V.E34S] + 2*Y[:,V.E44S] +
                    Y[:,V.E14I] + Y[:,V.E24I] + Y[:,V.E34I] + 2*Y[:,V.E44I] +
                    Y[:,V.E14R] + Y[:,V.E24R] + Y[:,V.E34R] + 2*Y[:,V.E44R] +
                    Y[:,V.E14T] + Y[:,V.E24T] + Y[:,V.E34T] + 2*Y[:,V.E44T]
                )
                self.simulations[observables.index('Phosphorylated_Akt'),:,i] = (
                    Y[:,V.Aktstar]
                )
                self.simulations[observables.index('Phosphorylated_ERK'),:,i] = (
                    (Y[:,V.pERKn] + Y[:,V.ppERKn])*(x[C.Vn]/x[C.Vc]) + Y[:,V.pERKc] + Y[:,V.ppERKc]
                )
                self.simulations[observables.index('Phosphorylated_cFos'),:,i] = (
                    Y[:,V.pcFOSn]*(x[C.Vn]/x[C.Vc]) + Y[:,V.pcFOSc]
                )
                self.simulations[observables.index('Phosphorylated_Shc'),:,i] = (
                    Y[:,V.sigmaSP] + Y[:,V.sigmaSP_G]
                )

class ExperimentalData(object):

    # ErbB receptors -----------------------------------------------------------
    t2 = [0, 300, 900, 1800, 2700, 3600, 5400, 7200]

    experiments = [None]*len(observables)

    experiments[observables.index('Phosphorylated_ErbB1')] = {
        'EGF':[
            296.021,
            1120.749,
            470.678,
            408.678,
            335.849,
            361.263,
            378.849,
            452.678,
        ],
        'HRG':[
            296.021,
            18178.451,
            15916.087,
            15522.137,
            15612.894,
            10524.823,
            7092.045,
            4946.853,
        ],
    }

    experiments[observables.index('Phosphorylated_ErbB2')] = {
        'EGF':[
            160.95,
            645.435,
            417.192,
            375.778,
            250.364,
            196.95,
            91.536,
            118.95,
        ],
        'HRG':[
            160.95,
            12593.681,
            10158.388,
            8388.853,
            10223.267,
            9802.146,
            6938.146,
            4817.196,
        ],
    }

    experiments[observables.index('Phosphorylated_ErbB3')] = {
        'EGF':[
            0,
            191.536,
            203.536,
            151.536,
            143.536,
            143.536,
            0,
            347.364,
        ],
        'HRG':[
            0,
            19106.773,
            18263.187,
            15984.48,
            14145.187,
            12654.359,
            9128.409,
            8480.874,
        ],
    }

    experiments[observables.index('Phosphorylated_ErbB4')] = {
        'EGF':[
            207.536,
            1677.678,
            1392.263,
            1439.092,
            1676.506,
            1013.435,
            764.021,
            565.192,
        ],
        'HRG':[
            207.536,
            20906.25,
            23330.2,
            23689.271,
            21652.099,
            13701.936,
            8715.53,
            3860.912,
        ],
    }
    # ErbB receptors -----------------------------------------------------------

    # Signal -------------------------------------------------------------------

    t = [0, 300, 1800, 3600, 5400, 7200]

    experiments[observables.index('Phosphorylated_Akt')] = {
        'EGF':[
            398.364,
            3135.376,
            505.192,
            618.607,
            653.192,
            988.021,
        ],
        'HRG':[
            398.364,
            13639.794,
            19250.2,
            23516.22,
            23677.635,
            20488.442,
        ],
        'EGF_U0126':[
            1369.849,
            3472.962,
            2499.477,
            2273.648,
            1699.335,
            2148.991,
        ],
        'HRG_U0126':[
            1369.849,
            14272.401,
            12633.986,
            14404.35,
            22673.635,
            25160.877,
        ],
    }

    experiments[observables.index('Phosphorylated_ERK')] = {
        'EGF':[
            1389.678,
            33683.505,
            12851.401,
            11140.329,
            8090.187,
            7936.945,
        ],
        'HRG':[
            1389.678,
            29926.191,
            31015.312,
            34110.798,
            32970.383,
            22076.392,
        ],
        'EGF_U0126':[
            847.536,
            348.95,
            3818.933,
            1723.577,
            1173.678,
            1034.849,
        ],
        'HRG_U0126':[
            847.536,
            979.778,
            21897.22,
            21949.978,
            21632.978,
            18214.25,
        ],
    }

    experiments[observables.index('Phosphorylated_cFos')] = {
        'EGF':[
            3604.711,
            5093.61,
            7051.217,
            8178.752,
            9056.581,
            6231.267,
        ],
        'HRG':[
            3604.711,
            3161.054,
            13496.43,
            16809.329,
            18557.572,
            15312.501,
        ],
        'EGF_U0126':[
            2160.962,
            1396.234,
            1639.477,
            1461.234,
            1225.991,
            947.335,
        ],
        'HRG_U0126':[
            2160.962,
            1278.82,
            4900.782,
            10561.116,
            15226.844,
            17369.865,
        ],
    }
    # --------------------------------------------------------------------------
    # pShc
    t3 = [0, 60, 120, 300, 600, 1800]
    experiments[observables.index('Phosphorylated_Shc')] = {
        'EGF':[0, 0.63634471, 0.690701763, 0.597348921, 0.577021971, 0.366298441],
        'HRG':[0, 0.861464472, 1, 0.908652428, 1.315086829, 1.797689176],
    }

    def get_timepoint(self,obs_idx):
        if obs_idx in [
            observables.index('Phosphorylated_ErbB1'),
            observables.index('Phosphorylated_ErbB2'),
            observables.index('Phosphorylated_ErbB3'),
            observables.index('Phosphorylated_ErbB4'),
            ]:
            exp_t = self.t2
        elif obs_idx in [observables.index('Phosphorylated_Shc')]:
            exp_t = self.t3
        else:
            exp_t = self.t

        return list(map(int,exp_t))
    """
    @staticmethod
    def get_norm_max(egf_data,hrg_data):
        diff_egf = np.array(egf_data) - egf_data[0]
        diff_hrg = np.array(hrg_data) - hrg_data[0]

        return np.max(np.maximum(diff_egf,diff_hrg))
    """
    @staticmethod
    def get_norm_max(egf_data,hrg_data):
        exp_min = np.min(
            np.append(
                egf_data,hrg_data
            )
        )
        diff_egf = np.array(egf_data) - exp_min
        diff_hrg = np.array(hrg_data) - exp_min

        return np.max(np.maximum(diff_egf,diff_hrg))