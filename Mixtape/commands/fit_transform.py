"""Subcommands of the `mixtape` script using the NumpydocClass command wrapper
"""
# Author: Robert McGibbon <rmcgibbo@gmail.com>
# Contributors:
# Copyright (c) 2014, Stanford University
# All rights reserved.

# Mixtape is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Mixtape. If not, see <http://www.gnu.org/licenses/>.

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from __future__ import print_function, absolute_import

import os

from ..utils.progressbar import ProgressBar, Percentage, Bar, ETA
from ..dataset import dataset
from ..utils import verbosedump
from ..decomposition import tICA, PCA
from ..cluster import (KMeans, KCenters, KMedoids, MiniBatchKMedoids,
                       MiniBatchKMeans)
from ..cmdline import NumpydocClassCommand, argument, exttype


class FitTransformCommand(NumpydocClassCommand):
    inp = argument(
        '--inp', help='''Input dataset. This should be serialized
        list of numpy arrays.''', required=True)
    out = argument(
        '--out', help='''Output (fit) model. This will be a
        serialized instance of the fit model object (optional).''',
        default='', type=exttype('.pkl'))
    transformed = argument(
        '--transformed', help='''Output (transformed)
        dataset. This will be a serialized list of numpy arrays,
        corresponding to each array in the input data set after the
        applied transformation (optional).''', default='', type=exttype('.h5'))

    def start(self):
        if self.out is '' and self.transformed is '':
            self.error('One of --out or --model should be specified')
        if self.transformed is not '' and os.path.exists(self.transformed):
            self.error('File exists: %s' % self.transformed)

        print(self.instance)

        inp_ds = dataset(self.inp, mode='r', verbose=False)
        print("Fitting model...")
        self.instance.fit(inp_ds)

        print("*********\n*RESULTS*\n*********")
        print(self.instance.summarize())
        print('-' * 80)

        if self.transformed is not '':
            out_ds = inp_ds.create_derived(self.transformed, fmt='hdf5')
            pbar = ProgressBar(
                widgets=['Transforming ', Percentage(), Bar(), ETA()],
                maxval=len(inp_ds)).start()

            for key in pbar(inp_ds.keys()):
                in_seq = inp_ds.get(key)
                out_ds[key] = self.instance.partial_transform(in_seq)

            print("\nSaving transformed dataset to '%s'" % self.transformed)
            print("To load this dataset interactive inside an IPython")
            print("shell or notebook, run\n")
            print("  $ ipython")
            print("  >>> from mixtape.dataset import dataset")
            print("  >>> ds = dataset('%s')\n" % self.transformed)

        if self.out is not '':
            verbosedump(self.instance, self.out)
            print("To load this %s object interactively inside an IPython\n"
                  "shell or notebook, run: \n" % self.klass.__name__)
            print("  $ ipython")
            print("  >>> from mixtape.utils import load")
            print("  >>> model = load('%s')\n" % self.out)


class tICACommand(FitTransformCommand):
    klass = tICA
    _concrete = True
    _group = '3-Decomposition'


class PCACommand(FitTransformCommand):
    klass = PCA
    _concrete = True
    _group = '3-Decomposition'


class KMeansCommand(FitTransformCommand):
    klass = KMeans
    _concrete = True
    _group = '2-Clustering'

    def _random_state_type(self, state):
        if state is None:
            return None
        return int(state)


class MiniBatchKMeansCommand(KMeansCommand):
    klass = MiniBatchKMeans
    _concrete = True
    _group = '2-Clustering'


class KCentersCommand(KMeansCommand):
    klass = KCenters
    _concrete = True
    _group = '2-Clustering'


class KMedoidsCommand(KMeansCommand):
    klass = KMedoids
    _concrete = True
    _group = '2-Clustering'


class MiniBatchKMedoidsCommand(KMeansCommand):
    klass = MiniBatchKMedoids
    _concrete = True
    _group = '2-Clustering'
