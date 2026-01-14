import os
import sys
import io
from contextlib import contextmanager

from mpi4py import MPI

from cython.operator cimport dereference
from libc.stdio cimport stdout
from libc.stdlib cimport malloc, free
from libc.string cimport strcmp
from numpy cimport ndarray
ctypedef double complex double_complex

from pyquda_comm.pointer cimport Pointer, Pointers, _NDArray
cimport quda


@contextmanager
def redirect_stdout(value: bytearray):
    stdout_fd = sys.stdout.fileno()
    stdout_dup_fd = os.dup(stdout_fd)
    pipe_out, pipe_in = os.pipe()
    os.dup2(pipe_in, stdout_fd)

    yield

    sys.stdout.write(b"\x00".decode(sys.stdout.encoding))
    sys.stdout.flush()
    os.close(pipe_in)
    with io.FileIO(pipe_out, closefd=True) as fio:
        buffer = fio.read(4096)
        while b"\00" not in buffer:
            value.extend(buffer)
            buffer = fio.read(4096)
        value.extend(buffer)
    os.dup2(stdout_dup_fd, stdout_fd)
    os.close(stdout_dup_fd)


cdef class QudaGaugeParam:
    cdef quda.QudaGaugeParam param

    def __init__(self):
        self.param = quda.newQudaGaugeParam()

    def __repr__(self):
        value = bytearray()
        with redirect_stdout(value):
            quda.printQudaGaugeParam(&self.param)
        return value.decode(sys.stdout.encoding)

    cdef from_ptr(self, quda.QudaGaugeParam *ptr):
        self.param = dereference(ptr)

    @property
    def struct_size(self):
        return self.param.struct_size

    @struct_size.setter
    def struct_size(self, value):
        self.param.struct_size = value

    @property
    def location(self):
        return self.param.location

    @location.setter
    def location(self, value):
        self.param.location = value

    @property
    def X(self):
        return self.param.X

    @X.setter
    def X(self, value):
        self.param.X = value

    @property
    def anisotropy(self):
        return self.param.anisotropy

    @anisotropy.setter
    def anisotropy(self, value):
        self.param.anisotropy = value

    @property
    def tadpole_coeff(self):
        return self.param.tadpole_coeff

    @tadpole_coeff.setter
    def tadpole_coeff(self, value):
        self.param.tadpole_coeff = value

    @property
    def scale(self):
        return self.param.scale

    @scale.setter
    def scale(self, value):
        self.param.scale = value

    @property
    def type(self):
        return self.param.type

    @type.setter
    def type(self, value):
        self.param.type = value

    @property
    def gauge_order(self):
        return self.param.gauge_order

    @gauge_order.setter
    def gauge_order(self, value):
        self.param.gauge_order = value

    @property
    def t_boundary(self):
        return self.param.t_boundary

    @t_boundary.setter
    def t_boundary(self, value):
        self.param.t_boundary = value

    @property
    def cpu_prec(self):
        return self.param.cpu_prec

    @cpu_prec.setter
    def cpu_prec(self, value):
        self.param.cpu_prec = value

    @property
    def cuda_prec(self):
        return self.param.cuda_prec

    @cuda_prec.setter
    def cuda_prec(self, value):
        self.param.cuda_prec = value

    @property
    def reconstruct(self):
        return self.param.reconstruct

    @reconstruct.setter
    def reconstruct(self, value):
        self.param.reconstruct = value

    @property
    def cuda_prec_sloppy(self):
        return self.param.cuda_prec_sloppy

    @cuda_prec_sloppy.setter
    def cuda_prec_sloppy(self, value):
        self.param.cuda_prec_sloppy = value

    @property
    def reconstruct_sloppy(self):
        return self.param.reconstruct_sloppy

    @reconstruct_sloppy.setter
    def reconstruct_sloppy(self, value):
        self.param.reconstruct_sloppy = value

    @property
    def cuda_prec_refinement_sloppy(self):
        return self.param.cuda_prec_refinement_sloppy

    @cuda_prec_refinement_sloppy.setter
    def cuda_prec_refinement_sloppy(self, value):
        self.param.cuda_prec_refinement_sloppy = value

    @property
    def reconstruct_refinement_sloppy(self):
        return self.param.reconstruct_refinement_sloppy

    @reconstruct_refinement_sloppy.setter
    def reconstruct_refinement_sloppy(self, value):
        self.param.reconstruct_refinement_sloppy = value

    @property
    def cuda_prec_precondition(self):
        return self.param.cuda_prec_precondition

    @cuda_prec_precondition.setter
    def cuda_prec_precondition(self, value):
        self.param.cuda_prec_precondition = value

    @property
    def reconstruct_precondition(self):
        return self.param.reconstruct_precondition

    @reconstruct_precondition.setter
    def reconstruct_precondition(self, value):
        self.param.reconstruct_precondition = value

    @property
    def cuda_prec_eigensolver(self):
        return self.param.cuda_prec_eigensolver

    @cuda_prec_eigensolver.setter
    def cuda_prec_eigensolver(self, value):
        self.param.cuda_prec_eigensolver = value

    @property
    def reconstruct_eigensolver(self):
        return self.param.reconstruct_eigensolver

    @reconstruct_eigensolver.setter
    def reconstruct_eigensolver(self, value):
        self.param.reconstruct_eigensolver = value

    @property
    def gauge_fix(self):
        return self.param.gauge_fix

    @gauge_fix.setter
    def gauge_fix(self, value):
        self.param.gauge_fix = value

    @property
    def ga_pad(self):
        return self.param.ga_pad

    @ga_pad.setter
    def ga_pad(self, value):
        self.param.ga_pad = value

    @property
    def site_ga_pad(self):
        return self.param.site_ga_pad

    @site_ga_pad.setter
    def site_ga_pad(self, value):
        self.param.site_ga_pad = value

    @property
    def staple_pad(self):
        return self.param.staple_pad

    @staple_pad.setter
    def staple_pad(self, value):
        self.param.staple_pad = value

    @property
    def llfat_ga_pad(self):
        return self.param.llfat_ga_pad

    @llfat_ga_pad.setter
    def llfat_ga_pad(self, value):
        self.param.llfat_ga_pad = value

    @property
    def mom_ga_pad(self):
        return self.param.mom_ga_pad

    @mom_ga_pad.setter
    def mom_ga_pad(self, value):
        self.param.mom_ga_pad = value

    @property
    def use_split_gauge_bkup(self):
        return self.param.use_split_gauge_bkup

    @use_split_gauge_bkup.setter
    def use_split_gauge_bkup(self, value):
        self.param.use_split_gauge_bkup = value

    @property
    def staggered_phase_type(self):
        return self.param.staggered_phase_type

    @staggered_phase_type.setter
    def staggered_phase_type(self, value):
        self.param.staggered_phase_type = value

    @property
    def staggered_phase_applied(self):
        return self.param.staggered_phase_applied

    @staggered_phase_applied.setter
    def staggered_phase_applied(self, value):
        self.param.staggered_phase_applied = value

    @property
    def i_mu(self):
        return self.param.i_mu

    @i_mu.setter
    def i_mu(self, value):
        self.param.i_mu = value

    @property
    def overlap(self):
        return self.param.overlap

    @overlap.setter
    def overlap(self, value):
        self.param.overlap = value

    @property
    def overwrite_gauge(self):
        return self.param.overwrite_gauge

    @overwrite_gauge.setter
    def overwrite_gauge(self, value):
        self.param.overwrite_gauge = value

    @property
    def overwrite_mom(self):
        return self.param.overwrite_mom

    @overwrite_mom.setter
    def overwrite_mom(self, value):
        self.param.overwrite_mom = value

    @property
    def use_resident_gauge(self):
        return self.param.use_resident_gauge

    @use_resident_gauge.setter
    def use_resident_gauge(self, value):
        self.param.use_resident_gauge = value

    @property
    def use_resident_mom(self):
        return self.param.use_resident_mom

    @use_resident_mom.setter
    def use_resident_mom(self, value):
        self.param.use_resident_mom = value

    @property
    def make_resident_gauge(self):
        return self.param.make_resident_gauge

    @make_resident_gauge.setter
    def make_resident_gauge(self, value):
        self.param.make_resident_gauge = value

    @property
    def make_resident_mom(self):
        return self.param.make_resident_mom

    @make_resident_mom.setter
    def make_resident_mom(self, value):
        self.param.make_resident_mom = value

    @property
    def return_result_gauge(self):
        return self.param.return_result_gauge

    @return_result_gauge.setter
    def return_result_gauge(self, value):
        self.param.return_result_gauge = value

    @property
    def return_result_mom(self):
        return self.param.return_result_mom

    @return_result_mom.setter
    def return_result_mom(self, value):
        self.param.return_result_mom = value

    @property
    def gauge_offset(self):
        return self.param.gauge_offset

    @gauge_offset.setter
    def gauge_offset(self, value):
        self.param.gauge_offset = value

    @property
    def mom_offset(self):
        return self.param.mom_offset

    @mom_offset.setter
    def mom_offset(self, value):
        self.param.mom_offset = value

    @property
    def site_size(self):
        return self.param.site_size

    @site_size.setter
    def site_size(self, value):
        self.param.site_size = value

cdef class QudaInvertParam:
    cdef quda.QudaInvertParam param

    def __init__(self):
        self.param = quda.newQudaInvertParam()

    def __repr__(self):
        value = bytearray()
        with redirect_stdout(value):
            quda.printQudaInvertParam(&self.param)
        return value.decode(sys.stdout.encoding)

    cdef from_ptr(self, quda.QudaInvertParam *ptr):
        self.param = dereference(ptr)

    @property
    def struct_size(self):
        return self.param.struct_size

    @struct_size.setter
    def struct_size(self, value):
        self.param.struct_size = value

    @property
    def input_location(self):
        return self.param.input_location

    @input_location.setter
    def input_location(self, value):
        self.param.input_location = value

    @property
    def output_location(self):
        return self.param.output_location

    @output_location.setter
    def output_location(self, value):
        self.param.output_location = value

    @property
    def dslash_type(self):
        return self.param.dslash_type

    @dslash_type.setter
    def dslash_type(self, value):
        self.param.dslash_type = value

    @property
    def inv_type(self):
        return self.param.inv_type

    @inv_type.setter
    def inv_type(self, value):
        self.param.inv_type = value

    @property
    def mass(self):
        return self.param.mass

    @mass.setter
    def mass(self, value):
        self.param.mass = value

    @property
    def kappa(self):
        return self.param.kappa

    @kappa.setter
    def kappa(self, value):
        self.param.kappa = value

    @property
    def m5(self):
        return self.param.m5

    @m5.setter
    def m5(self, value):
        self.param.m5 = value

    @property
    def Ls(self):
        return self.param.Ls

    @Ls.setter
    def Ls(self, value):
        self.param.Ls = value

    @property
    def b_5(self):
        return self.param.b_5

    @b_5.setter
    def b_5(self, value):
        self.param.b_5 = value

    @property
    def c_5(self):
        return self.param.c_5

    @c_5.setter
    def c_5(self, value):
        self.param.c_5 = value

    @property
    def eofa_shift(self):
        return self.param.eofa_shift

    @eofa_shift.setter
    def eofa_shift(self, value):
        self.param.eofa_shift = value

    @property
    def eofa_pm(self):
        return self.param.eofa_pm

    @eofa_pm.setter
    def eofa_pm(self, value):
        self.param.eofa_pm = value

    @property
    def mq1(self):
        return self.param.mq1

    @mq1.setter
    def mq1(self, value):
        self.param.mq1 = value

    @property
    def mq2(self):
        return self.param.mq2

    @mq2.setter
    def mq2(self, value):
        self.param.mq2 = value

    @property
    def mq3(self):
        return self.param.mq3

    @mq3.setter
    def mq3(self, value):
        self.param.mq3 = value

    @property
    def mu(self):
        return self.param.mu

    @mu.setter
    def mu(self, value):
        self.param.mu = value

    @property
    def tm_rho(self):
        return self.param.tm_rho

    @tm_rho.setter
    def tm_rho(self, value):
        self.param.tm_rho = value

    @property
    def epsilon(self):
        return self.param.epsilon

    @epsilon.setter
    def epsilon(self, value):
        self.param.epsilon = value

    @property
    def evmax(self):
        return self.param.evmax

    @evmax.setter
    def evmax(self, value):
        self.param.evmax = value

    @property
    def twist_flavor(self):
        return self.param.twist_flavor

    @twist_flavor.setter
    def twist_flavor(self, value):
        self.param.twist_flavor = value

    @property
    def laplace3D(self):
        return self.param.laplace3D

    @laplace3D.setter
    def laplace3D(self, value):
        self.param.laplace3D = value

    @property
    def covdev_mu(self):
        return self.param.covdev_mu

    @covdev_mu.setter
    def covdev_mu(self, value):
        self.param.covdev_mu = value

    @property
    def tol(self):
        return self.param.tol

    @tol.setter
    def tol(self, value):
        self.param.tol = value

    @property
    def tol_restart(self):
        return self.param.tol_restart

    @tol_restart.setter
    def tol_restart(self, value):
        self.param.tol_restart = value

    @property
    def tol_hq(self):
        return self.param.tol_hq

    @tol_hq.setter
    def tol_hq(self, value):
        self.param.tol_hq = value

    @property
    def compute_true_res(self):
        return self.param.compute_true_res

    @compute_true_res.setter
    def compute_true_res(self, value):
        self.param.compute_true_res = value

    @property
    def true_res(self):
        return self.param.true_res

    @true_res.setter
    def true_res(self, value):
        self.param.true_res = value

    @property
    def true_res_hq(self):
        return self.param.true_res_hq

    @true_res_hq.setter
    def true_res_hq(self, value):
        self.param.true_res_hq = value

    @property
    def maxiter(self):
        return self.param.maxiter

    @maxiter.setter
    def maxiter(self, value):
        self.param.maxiter = value

    @property
    def reliable_delta(self):
        return self.param.reliable_delta

    @reliable_delta.setter
    def reliable_delta(self, value):
        self.param.reliable_delta = value

    @property
    def reliable_delta_refinement(self):
        return self.param.reliable_delta_refinement

    @reliable_delta_refinement.setter
    def reliable_delta_refinement(self, value):
        self.param.reliable_delta_refinement = value

    @property
    def use_alternative_reliable(self):
        return self.param.use_alternative_reliable

    @use_alternative_reliable.setter
    def use_alternative_reliable(self, value):
        self.param.use_alternative_reliable = value

    @property
    def use_sloppy_partial_accumulator(self):
        return self.param.use_sloppy_partial_accumulator

    @use_sloppy_partial_accumulator.setter
    def use_sloppy_partial_accumulator(self, value):
        self.param.use_sloppy_partial_accumulator = value

    @property
    def solution_accumulator_pipeline(self):
        return self.param.solution_accumulator_pipeline

    @solution_accumulator_pipeline.setter
    def solution_accumulator_pipeline(self, value):
        self.param.solution_accumulator_pipeline = value

    @property
    def max_res_increase(self):
        return self.param.max_res_increase

    @max_res_increase.setter
    def max_res_increase(self, value):
        self.param.max_res_increase = value

    @property
    def max_res_increase_total(self):
        return self.param.max_res_increase_total

    @max_res_increase_total.setter
    def max_res_increase_total(self, value):
        self.param.max_res_increase_total = value

    @property
    def max_hq_res_increase(self):
        return self.param.max_hq_res_increase

    @max_hq_res_increase.setter
    def max_hq_res_increase(self, value):
        self.param.max_hq_res_increase = value

    @property
    def max_hq_res_restart_total(self):
        return self.param.max_hq_res_restart_total

    @max_hq_res_restart_total.setter
    def max_hq_res_restart_total(self, value):
        self.param.max_hq_res_restart_total = value

    @property
    def heavy_quark_check(self):
        return self.param.heavy_quark_check

    @heavy_quark_check.setter
    def heavy_quark_check(self, value):
        self.param.heavy_quark_check = value

    @property
    def pipeline(self):
        return self.param.pipeline

    @pipeline.setter
    def pipeline(self, value):
        self.param.pipeline = value

    @property
    def num_offset(self):
        return self.param.num_offset

    @num_offset.setter
    def num_offset(self, value):
        self.param.num_offset = value

    @property
    def num_src(self):
        return self.param.num_src

    @num_src.setter
    def num_src(self, value):
        self.param.num_src = value

    @property
    def num_src_per_sub_partition(self):
        return self.param.num_src_per_sub_partition

    @num_src_per_sub_partition.setter
    def num_src_per_sub_partition(self, value):
        self.param.num_src_per_sub_partition = value

    @property
    def split_grid(self):
        return self.param.split_grid

    @split_grid.setter
    def split_grid(self, value):
        self.param.split_grid = value

    @property
    def overlap(self):
        return self.param.overlap

    @overlap.setter
    def overlap(self, value):
        self.param.overlap = value

    @property
    def offset(self):
        return self.param.offset

    @offset.setter
    def offset(self, value):
        self.param.offset = value

    @property
    def tol_offset(self):
        return self.param.tol_offset

    @tol_offset.setter
    def tol_offset(self, value):
        self.param.tol_offset = value

    @property
    def tol_hq_offset(self):
        return self.param.tol_hq_offset

    @tol_hq_offset.setter
    def tol_hq_offset(self, value):
        self.param.tol_hq_offset = value

    @property
    def true_res_offset(self):
        return self.param.true_res_offset

    @true_res_offset.setter
    def true_res_offset(self, value):
        self.param.true_res_offset = value

    @property
    def iter_res_offset(self):
        return self.param.iter_res_offset

    @iter_res_offset.setter
    def iter_res_offset(self, value):
        self.param.iter_res_offset = value

    @property
    def true_res_hq_offset(self):
        return self.param.true_res_hq_offset

    @true_res_hq_offset.setter
    def true_res_hq_offset(self, value):
        self.param.true_res_hq_offset = value

    @property
    def residue(self):
        return self.param.residue

    @residue.setter
    def residue(self, value):
        self.param.residue = value

    @property
    def compute_action(self):
        return self.param.compute_action

    @compute_action.setter
    def compute_action(self, value):
        self.param.compute_action = value

    @property
    def action(self):
        return self.param.action

    @action.setter
    def action(self, value):
        self.param.action = value

    @property
    def solution_type(self):
        return self.param.solution_type

    @solution_type.setter
    def solution_type(self, value):
        self.param.solution_type = value

    @property
    def solve_type(self):
        return self.param.solve_type

    @solve_type.setter
    def solve_type(self, value):
        self.param.solve_type = value

    @property
    def matpc_type(self):
        return self.param.matpc_type

    @matpc_type.setter
    def matpc_type(self, value):
        self.param.matpc_type = value

    @property
    def dagger(self):
        return self.param.dagger

    @dagger.setter
    def dagger(self, value):
        self.param.dagger = value

    @property
    def mass_normalization(self):
        return self.param.mass_normalization

    @mass_normalization.setter
    def mass_normalization(self, value):
        self.param.mass_normalization = value

    @property
    def solver_normalization(self):
        return self.param.solver_normalization

    @solver_normalization.setter
    def solver_normalization(self, value):
        self.param.solver_normalization = value

    @property
    def preserve_source(self):
        return self.param.preserve_source

    @preserve_source.setter
    def preserve_source(self, value):
        self.param.preserve_source = value

    @property
    def cpu_prec(self):
        return self.param.cpu_prec

    @cpu_prec.setter
    def cpu_prec(self, value):
        self.param.cpu_prec = value

    @property
    def cuda_prec(self):
        return self.param.cuda_prec

    @cuda_prec.setter
    def cuda_prec(self, value):
        self.param.cuda_prec = value

    @property
    def cuda_prec_sloppy(self):
        return self.param.cuda_prec_sloppy

    @cuda_prec_sloppy.setter
    def cuda_prec_sloppy(self, value):
        self.param.cuda_prec_sloppy = value

    @property
    def cuda_prec_refinement_sloppy(self):
        return self.param.cuda_prec_refinement_sloppy

    @cuda_prec_refinement_sloppy.setter
    def cuda_prec_refinement_sloppy(self, value):
        self.param.cuda_prec_refinement_sloppy = value

    @property
    def cuda_prec_precondition(self):
        return self.param.cuda_prec_precondition

    @cuda_prec_precondition.setter
    def cuda_prec_precondition(self, value):
        self.param.cuda_prec_precondition = value

    @property
    def cuda_prec_eigensolver(self):
        return self.param.cuda_prec_eigensolver

    @cuda_prec_eigensolver.setter
    def cuda_prec_eigensolver(self, value):
        self.param.cuda_prec_eigensolver = value

    @property
    def dirac_order(self):
        return self.param.dirac_order

    @dirac_order.setter
    def dirac_order(self, value):
        self.param.dirac_order = value

    @property
    def gamma_basis(self):
        return self.param.gamma_basis

    @gamma_basis.setter
    def gamma_basis(self, value):
        self.param.gamma_basis = value

    @property
    def clover_location(self):
        return self.param.clover_location

    @clover_location.setter
    def clover_location(self, value):
        self.param.clover_location = value

    @property
    def clover_cpu_prec(self):
        return self.param.clover_cpu_prec

    @clover_cpu_prec.setter
    def clover_cpu_prec(self, value):
        self.param.clover_cpu_prec = value

    @property
    def clover_cuda_prec(self):
        return self.param.clover_cuda_prec

    @clover_cuda_prec.setter
    def clover_cuda_prec(self, value):
        self.param.clover_cuda_prec = value

    @property
    def clover_cuda_prec_sloppy(self):
        return self.param.clover_cuda_prec_sloppy

    @clover_cuda_prec_sloppy.setter
    def clover_cuda_prec_sloppy(self, value):
        self.param.clover_cuda_prec_sloppy = value

    @property
    def clover_cuda_prec_refinement_sloppy(self):
        return self.param.clover_cuda_prec_refinement_sloppy

    @clover_cuda_prec_refinement_sloppy.setter
    def clover_cuda_prec_refinement_sloppy(self, value):
        self.param.clover_cuda_prec_refinement_sloppy = value

    @property
    def clover_cuda_prec_precondition(self):
        return self.param.clover_cuda_prec_precondition

    @clover_cuda_prec_precondition.setter
    def clover_cuda_prec_precondition(self, value):
        self.param.clover_cuda_prec_precondition = value

    @property
    def clover_cuda_prec_eigensolver(self):
        return self.param.clover_cuda_prec_eigensolver

    @clover_cuda_prec_eigensolver.setter
    def clover_cuda_prec_eigensolver(self, value):
        self.param.clover_cuda_prec_eigensolver = value

    @property
    def clover_order(self):
        return self.param.clover_order

    @clover_order.setter
    def clover_order(self, value):
        self.param.clover_order = value

    @property
    def use_init_guess(self):
        return self.param.use_init_guess

    @use_init_guess.setter
    def use_init_guess(self, value):
        self.param.use_init_guess = value

    @property
    def clover_csw(self):
        return self.param.clover_csw

    @clover_csw.setter
    def clover_csw(self, value):
        self.param.clover_csw = value

    @property
    def clover_coeff(self):
        return self.param.clover_coeff

    @clover_coeff.setter
    def clover_coeff(self, value):
        self.param.clover_coeff = value

    @property
    def clover_rho(self):
        return self.param.clover_rho

    @clover_rho.setter
    def clover_rho(self, value):
        self.param.clover_rho = value

    @property
    def compute_clover_trlog(self):
        return self.param.compute_clover_trlog

    @compute_clover_trlog.setter
    def compute_clover_trlog(self, value):
        self.param.compute_clover_trlog = value

    @property
    def trlogA(self):
        return self.param.trlogA

    @trlogA.setter
    def trlogA(self, value):
        self.param.trlogA = value

    @property
    def compute_clover(self):
        return self.param.compute_clover

    @compute_clover.setter
    def compute_clover(self, value):
        self.param.compute_clover = value

    @property
    def compute_clover_inverse(self):
        return self.param.compute_clover_inverse

    @compute_clover_inverse.setter
    def compute_clover_inverse(self, value):
        self.param.compute_clover_inverse = value

    @property
    def return_clover(self):
        return self.param.return_clover

    @return_clover.setter
    def return_clover(self, value):
        self.param.return_clover = value

    @property
    def return_clover_inverse(self):
        return self.param.return_clover_inverse

    @return_clover_inverse.setter
    def return_clover_inverse(self, value):
        self.param.return_clover_inverse = value

    @property
    def verbosity(self):
        return self.param.verbosity

    @verbosity.setter
    def verbosity(self, value):
        self.param.verbosity = value

    @property
    def iter(self):
        return self.param.iter

    @iter.setter
    def iter(self, value):
        self.param.iter = value

    @property
    def gflops(self):
        return self.param.gflops

    @gflops.setter
    def gflops(self, value):
        self.param.gflops = value

    @property
    def secs(self):
        return self.param.secs

    @secs.setter
    def secs(self, value):
        self.param.secs = value

    @property
    def energy(self):
        return self.param.energy

    @energy.setter
    def energy(self, value):
        self.param.energy = value

    @property
    def power(self):
        return self.param.power

    @power.setter
    def power(self, value):
        self.param.power = value

    @property
    def temp(self):
        return self.param.temp

    @temp.setter
    def temp(self, value):
        self.param.temp = value

    @property
    def clock(self):
        return self.param.clock

    @clock.setter
    def clock(self, value):
        self.param.clock = value

    @property
    def Nsteps(self):
        return self.param.Nsteps

    @Nsteps.setter
    def Nsteps(self, value):
        self.param.Nsteps = value

    @property
    def gcrNkrylov(self):
        return self.param.gcrNkrylov

    @gcrNkrylov.setter
    def gcrNkrylov(self, value):
        self.param.gcrNkrylov = value

    @property
    def inv_type_precondition(self):
        return self.param.inv_type_precondition

    @inv_type_precondition.setter
    def inv_type_precondition(self, value):
        self.param.inv_type_precondition = value

    @property
    def preconditioner(self):
        ptr = Pointer("void")
        ptr.set_ptr(self.param.preconditioner)
        return ptr

    @preconditioner.setter
    def preconditioner(self, Pointer value):
        assert value.dtype == "void"
        self.param.preconditioner = value.ptr

    @property
    def deflation_op(self):
        ptr = Pointer("void")
        ptr.set_ptr(self.param.deflation_op)
        return ptr

    @deflation_op.setter
    def deflation_op(self, Pointer value):
        assert value.dtype == "void"
        self.param.deflation_op = value.ptr

    @property
    def eig_param(self):
        ptr = Pointer("void")
        ptr.set_ptr(self.param.eig_param)
        return ptr

    @eig_param.setter
    def eig_param(self, Pointer value):
        assert value.dtype == "void"
        self.param.eig_param = value.ptr

    @property
    def deflate(self):
        return self.param.deflate

    @deflate.setter
    def deflate(self, value):
        self.param.deflate = value

    @property
    def dslash_type_precondition(self):
        return self.param.dslash_type_precondition

    @dslash_type_precondition.setter
    def dslash_type_precondition(self, value):
        self.param.dslash_type_precondition = value

    @property
    def verbosity_precondition(self):
        return self.param.verbosity_precondition

    @verbosity_precondition.setter
    def verbosity_precondition(self, value):
        self.param.verbosity_precondition = value

    @property
    def tol_precondition(self):
        return self.param.tol_precondition

    @tol_precondition.setter
    def tol_precondition(self, value):
        self.param.tol_precondition = value

    @property
    def maxiter_precondition(self):
        return self.param.maxiter_precondition

    @maxiter_precondition.setter
    def maxiter_precondition(self, value):
        self.param.maxiter_precondition = value

    @property
    def omega(self):
        return self.param.omega

    @omega.setter
    def omega(self, value):
        self.param.omega = value

    @property
    def ca_basis(self):
        return self.param.ca_basis

    @ca_basis.setter
    def ca_basis(self, value):
        self.param.ca_basis = value

    @property
    def ca_lambda_min(self):
        return self.param.ca_lambda_min

    @ca_lambda_min.setter
    def ca_lambda_min(self, value):
        self.param.ca_lambda_min = value

    @property
    def ca_lambda_max(self):
        return self.param.ca_lambda_max

    @ca_lambda_max.setter
    def ca_lambda_max(self, value):
        self.param.ca_lambda_max = value

    @property
    def ca_basis_precondition(self):
        return self.param.ca_basis_precondition

    @ca_basis_precondition.setter
    def ca_basis_precondition(self, value):
        self.param.ca_basis_precondition = value

    @property
    def ca_lambda_min_precondition(self):
        return self.param.ca_lambda_min_precondition

    @ca_lambda_min_precondition.setter
    def ca_lambda_min_precondition(self, value):
        self.param.ca_lambda_min_precondition = value

    @property
    def ca_lambda_max_precondition(self):
        return self.param.ca_lambda_max_precondition

    @ca_lambda_max_precondition.setter
    def ca_lambda_max_precondition(self, value):
        self.param.ca_lambda_max_precondition = value

    @property
    def precondition_cycle(self):
        return self.param.precondition_cycle

    @precondition_cycle.setter
    def precondition_cycle(self, value):
        self.param.precondition_cycle = value

    @property
    def schwarz_type(self):
        return self.param.schwarz_type

    @schwarz_type.setter
    def schwarz_type(self, value):
        self.param.schwarz_type = value

    @property
    def accelerator_type_precondition(self):
        return self.param.accelerator_type_precondition

    @accelerator_type_precondition.setter
    def accelerator_type_precondition(self, value):
        self.param.accelerator_type_precondition = value

    @property
    def madwf_diagonal_suppressor(self):
        return self.param.madwf_diagonal_suppressor

    @madwf_diagonal_suppressor.setter
    def madwf_diagonal_suppressor(self, value):
        self.param.madwf_diagonal_suppressor = value

    @property
    def madwf_ls(self):
        return self.param.madwf_ls

    @madwf_ls.setter
    def madwf_ls(self, value):
        self.param.madwf_ls = value

    @property
    def madwf_null_miniter(self):
        return self.param.madwf_null_miniter

    @madwf_null_miniter.setter
    def madwf_null_miniter(self, value):
        self.param.madwf_null_miniter = value

    @property
    def madwf_null_tol(self):
        return self.param.madwf_null_tol

    @madwf_null_tol.setter
    def madwf_null_tol(self, value):
        self.param.madwf_null_tol = value

    @property
    def madwf_train_maxiter(self):
        return self.param.madwf_train_maxiter

    @madwf_train_maxiter.setter
    def madwf_train_maxiter(self, value):
        self.param.madwf_train_maxiter = value

    @property
    def madwf_param_load(self):
        return self.param.madwf_param_load

    @madwf_param_load.setter
    def madwf_param_load(self, value):
        self.param.madwf_param_load = value

    @property
    def madwf_param_save(self):
        return self.param.madwf_param_save

    @madwf_param_save.setter
    def madwf_param_save(self, value):
        self.param.madwf_param_save = value

    @property
    def madwf_param_infile(self):
        return self.param.madwf_param_infile

    @madwf_param_infile.setter
    def madwf_param_infile(self, const char value[]):
        self.param.madwf_param_infile = value

    @property
    def madwf_param_outfile(self):
        return self.param.madwf_param_outfile

    @madwf_param_outfile.setter
    def madwf_param_outfile(self, const char value[]):
        self.param.madwf_param_outfile = value

    @property
    def residual_type(self):
        return self.param.residual_type

    @residual_type.setter
    def residual_type(self, value):
        self.param.residual_type = value

    @property
    def cuda_prec_ritz(self):
        return self.param.cuda_prec_ritz

    @cuda_prec_ritz.setter
    def cuda_prec_ritz(self, value):
        self.param.cuda_prec_ritz = value

    @property
    def n_ev(self):
        return self.param.n_ev

    @n_ev.setter
    def n_ev(self, value):
        self.param.n_ev = value

    @property
    def max_search_dim(self):
        return self.param.max_search_dim

    @max_search_dim.setter
    def max_search_dim(self, value):
        self.param.max_search_dim = value

    @property
    def rhs_idx(self):
        return self.param.rhs_idx

    @rhs_idx.setter
    def rhs_idx(self, value):
        self.param.rhs_idx = value

    @property
    def deflation_grid(self):
        return self.param.deflation_grid

    @deflation_grid.setter
    def deflation_grid(self, value):
        self.param.deflation_grid = value

    @property
    def eigenval_tol(self):
        return self.param.eigenval_tol

    @eigenval_tol.setter
    def eigenval_tol(self, value):
        self.param.eigenval_tol = value

    @property
    def eigcg_max_restarts(self):
        return self.param.eigcg_max_restarts

    @eigcg_max_restarts.setter
    def eigcg_max_restarts(self, value):
        self.param.eigcg_max_restarts = value

    @property
    def max_restart_num(self):
        return self.param.max_restart_num

    @max_restart_num.setter
    def max_restart_num(self, value):
        self.param.max_restart_num = value

    @property
    def inc_tol(self):
        return self.param.inc_tol

    @inc_tol.setter
    def inc_tol(self, value):
        self.param.inc_tol = value

    @property
    def make_resident_solution(self):
        return self.param.make_resident_solution

    @make_resident_solution.setter
    def make_resident_solution(self, value):
        self.param.make_resident_solution = value

    @property
    def use_resident_solution(self):
        return self.param.use_resident_solution

    @use_resident_solution.setter
    def use_resident_solution(self, value):
        self.param.use_resident_solution = value

    @property
    def chrono_make_resident(self):
        return self.param.chrono_make_resident

    @chrono_make_resident.setter
    def chrono_make_resident(self, value):
        self.param.chrono_make_resident = value

    @property
    def chrono_replace_last(self):
        return self.param.chrono_replace_last

    @chrono_replace_last.setter
    def chrono_replace_last(self, value):
        self.param.chrono_replace_last = value

    @property
    def chrono_use_resident(self):
        return self.param.chrono_use_resident

    @chrono_use_resident.setter
    def chrono_use_resident(self, value):
        self.param.chrono_use_resident = value

    @property
    def chrono_max_dim(self):
        return self.param.chrono_max_dim

    @chrono_max_dim.setter
    def chrono_max_dim(self, value):
        self.param.chrono_max_dim = value

    @property
    def chrono_index(self):
        return self.param.chrono_index

    @chrono_index.setter
    def chrono_index(self, value):
        self.param.chrono_index = value

    @property
    def chrono_precision(self):
        return self.param.chrono_precision

    @chrono_precision.setter
    def chrono_precision(self, value):
        self.param.chrono_precision = value

    @property
    def extlib_type(self):
        return self.param.extlib_type

    @extlib_type.setter
    def extlib_type(self, value):
        self.param.extlib_type = value

    @property
    def native_blas_lapack(self):
        return self.param.native_blas_lapack

    @native_blas_lapack.setter
    def native_blas_lapack(self, value):
        self.param.native_blas_lapack = value

    @property
    def use_mobius_fused_kernel(self):
        return self.param.use_mobius_fused_kernel

    @use_mobius_fused_kernel.setter
    def use_mobius_fused_kernel(self, value):
        self.param.use_mobius_fused_kernel = value

    @property
    def distance_pc_alpha0(self):
        return self.param.distance_pc_alpha0

    @distance_pc_alpha0.setter
    def distance_pc_alpha0(self, value):
        self.param.distance_pc_alpha0 = value

    @property
    def distance_pc_t0(self):
        return self.param.distance_pc_t0

    @distance_pc_t0.setter
    def distance_pc_t0(self, value):
        self.param.distance_pc_t0 = value

    @property
    def additional_prop(self):
        ptr = Pointer("void")
        ptr.set_ptr(self.param.additional_prop)
        return ptr

    @additional_prop.setter
    def additional_prop(self, Pointer value):
        assert value.dtype == "void"
        self.param.additional_prop = value.ptr

cdef class QudaMultigridParam:
    cdef quda.QudaMultigridParam param

    def __init__(self):
        self.param = quda.newQudaMultigridParam()

    def __repr__(self):
        value = bytearray()
        with redirect_stdout(value):
            quda.printQudaMultigridParam(&self.param)
        return value.decode(sys.stdout.encoding)

    cdef from_ptr(self, quda.QudaMultigridParam *ptr):
        self.param = dereference(ptr)

    @property
    def struct_size(self):
        return self.param.struct_size

    @struct_size.setter
    def struct_size(self, value):
        self.param.struct_size = value

    @property
    def invert_param(self):
        param = QudaInvertParam()
        param.from_ptr(self.param.invert_param)
        return param

    @invert_param.setter
    def invert_param(self, value):
        self.set_invert_param(value)

    cdef set_invert_param(self, QudaInvertParam value):
        self.param.invert_param = &value.param

    @property
    def eig_param(self):
        params = []
        for i in range(self.param.n_level):
            if self.param.eig_param[i] != NULL:
                param = QudaEigParam()
                param.from_ptr(self.param.eig_param[i])
                params.append(param)
            else:
                params.append(None)
        return params

    @eig_param.setter
    def eig_param(self, value):
        for i in range(self.param.n_level):
            if value[i] is not None:
                self.set_eig_param(value[i], i)
            else:
                self.param.eig_param[i] = NULL

    cdef set_eig_param(self, QudaEigParam value, int i):
        self.param.eig_param[i] = &value.param

    @property
    def n_level(self):
        return self.param.n_level

    @n_level.setter
    def n_level(self, value):
        self.param.n_level = value

    @property
    def geo_block_size(self):
        value = []
        for i in range(self.n_level):
            value.append(self.param.geo_block_size[i])
        return value

    @geo_block_size.setter
    def geo_block_size(self, value):
        for i in range(self.n_level):
            self.param.geo_block_size[i] = value[i]

    @property
    def spin_block_size(self):
        return self.param.spin_block_size

    @spin_block_size.setter
    def spin_block_size(self, value):
        self.param.spin_block_size = value

    @property
    def n_vec(self):
        return self.param.n_vec

    @n_vec.setter
    def n_vec(self, value):
        self.param.n_vec = value

    @property
    def precision_null(self):
        return self.param.precision_null

    @precision_null.setter
    def precision_null(self, value):
        self.param.precision_null = value

    @property
    def n_block_ortho(self):
        return self.param.n_block_ortho

    @n_block_ortho.setter
    def n_block_ortho(self, value):
        self.param.n_block_ortho = value

    @property
    def block_ortho_two_pass(self):
        return self.param.block_ortho_two_pass

    @block_ortho_two_pass.setter
    def block_ortho_two_pass(self, value):
        self.param.block_ortho_two_pass = value

    @property
    def verbosity(self):
        return self.param.verbosity

    @verbosity.setter
    def verbosity(self, value):
        self.param.verbosity = value

    @property
    def setup_use_mma(self):
        return self.param.setup_use_mma

    @setup_use_mma.setter
    def setup_use_mma(self, value):
        self.param.setup_use_mma = value

    @property
    def dslash_use_mma(self):
        return self.param.dslash_use_mma

    @dslash_use_mma.setter
    def dslash_use_mma(self, value):
        self.param.dslash_use_mma = value

    @property
    def transfer_use_mma(self):
        return self.param.transfer_use_mma

    @transfer_use_mma.setter
    def transfer_use_mma(self, value):
        self.param.transfer_use_mma = value

    @property
    def setup_inv_type(self):
        return self.param.setup_inv_type

    @setup_inv_type.setter
    def setup_inv_type(self, value):
        self.param.setup_inv_type = value

    @property
    def n_vec_batch(self):
        return self.param.n_vec_batch

    @n_vec_batch.setter
    def n_vec_batch(self, value):
        self.param.n_vec_batch = value

    @property
    def num_setup_iter(self):
        return self.param.num_setup_iter

    @num_setup_iter.setter
    def num_setup_iter(self, value):
        self.param.num_setup_iter = value

    @property
    def setup_tol(self):
        return self.param.setup_tol

    @setup_tol.setter
    def setup_tol(self, value):
        self.param.setup_tol = value

    @property
    def setup_maxiter(self):
        return self.param.setup_maxiter

    @setup_maxiter.setter
    def setup_maxiter(self, value):
        self.param.setup_maxiter = value

    @property
    def setup_maxiter_refresh(self):
        return self.param.setup_maxiter_refresh

    @setup_maxiter_refresh.setter
    def setup_maxiter_refresh(self, value):
        self.param.setup_maxiter_refresh = value

    @property
    def setup_ca_basis(self):
        return self.param.setup_ca_basis

    @setup_ca_basis.setter
    def setup_ca_basis(self, value):
        self.param.setup_ca_basis = value

    @property
    def setup_ca_basis_size(self):
        return self.param.setup_ca_basis_size

    @setup_ca_basis_size.setter
    def setup_ca_basis_size(self, value):
        self.param.setup_ca_basis_size = value

    @property
    def setup_ca_lambda_min(self):
        return self.param.setup_ca_lambda_min

    @setup_ca_lambda_min.setter
    def setup_ca_lambda_min(self, value):
        self.param.setup_ca_lambda_min = value

    @property
    def setup_ca_lambda_max(self):
        return self.param.setup_ca_lambda_max

    @setup_ca_lambda_max.setter
    def setup_ca_lambda_max(self, value):
        self.param.setup_ca_lambda_max = value

    @property
    def setup_type(self):
        return self.param.setup_type

    @setup_type.setter
    def setup_type(self, value):
        self.param.setup_type = value

    @property
    def pre_orthonormalize(self):
        return self.param.pre_orthonormalize

    @pre_orthonormalize.setter
    def pre_orthonormalize(self, value):
        self.param.pre_orthonormalize = value

    @property
    def post_orthonormalize(self):
        return self.param.post_orthonormalize

    @post_orthonormalize.setter
    def post_orthonormalize(self, value):
        self.param.post_orthonormalize = value

    @property
    def coarse_solver(self):
        return self.param.coarse_solver

    @coarse_solver.setter
    def coarse_solver(self, value):
        self.param.coarse_solver = value

    @property
    def coarse_solver_tol(self):
        return self.param.coarse_solver_tol

    @coarse_solver_tol.setter
    def coarse_solver_tol(self, value):
        self.param.coarse_solver_tol = value

    @property
    def coarse_solver_maxiter(self):
        return self.param.coarse_solver_maxiter

    @coarse_solver_maxiter.setter
    def coarse_solver_maxiter(self, value):
        self.param.coarse_solver_maxiter = value

    @property
    def coarse_solver_ca_basis(self):
        return self.param.coarse_solver_ca_basis

    @coarse_solver_ca_basis.setter
    def coarse_solver_ca_basis(self, value):
        self.param.coarse_solver_ca_basis = value

    @property
    def coarse_solver_ca_basis_size(self):
        return self.param.coarse_solver_ca_basis_size

    @coarse_solver_ca_basis_size.setter
    def coarse_solver_ca_basis_size(self, value):
        self.param.coarse_solver_ca_basis_size = value

    @property
    def coarse_solver_ca_lambda_min(self):
        return self.param.coarse_solver_ca_lambda_min

    @coarse_solver_ca_lambda_min.setter
    def coarse_solver_ca_lambda_min(self, value):
        self.param.coarse_solver_ca_lambda_min = value

    @property
    def coarse_solver_ca_lambda_max(self):
        return self.param.coarse_solver_ca_lambda_max

    @coarse_solver_ca_lambda_max.setter
    def coarse_solver_ca_lambda_max(self, value):
        self.param.coarse_solver_ca_lambda_max = value

    @property
    def smoother(self):
        return self.param.smoother

    @smoother.setter
    def smoother(self, value):
        self.param.smoother = value

    @property
    def smoother_tol(self):
        return self.param.smoother_tol

    @smoother_tol.setter
    def smoother_tol(self, value):
        self.param.smoother_tol = value

    @property
    def nu_pre(self):
        return self.param.nu_pre

    @nu_pre.setter
    def nu_pre(self, value):
        self.param.nu_pre = value

    @property
    def nu_post(self):
        return self.param.nu_post

    @nu_post.setter
    def nu_post(self, value):
        self.param.nu_post = value

    @property
    def smoother_solver_ca_basis(self):
        return self.param.smoother_solver_ca_basis

    @smoother_solver_ca_basis.setter
    def smoother_solver_ca_basis(self, value):
        self.param.smoother_solver_ca_basis = value

    @property
    def smoother_solver_ca_lambda_min(self):
        return self.param.smoother_solver_ca_lambda_min

    @smoother_solver_ca_lambda_min.setter
    def smoother_solver_ca_lambda_min(self, value):
        self.param.smoother_solver_ca_lambda_min = value

    @property
    def smoother_solver_ca_lambda_max(self):
        return self.param.smoother_solver_ca_lambda_max

    @smoother_solver_ca_lambda_max.setter
    def smoother_solver_ca_lambda_max(self, value):
        self.param.smoother_solver_ca_lambda_max = value

    @property
    def omega(self):
        return self.param.omega

    @omega.setter
    def omega(self, value):
        self.param.omega = value

    @property
    def smoother_halo_precision(self):
        return self.param.smoother_halo_precision

    @smoother_halo_precision.setter
    def smoother_halo_precision(self, value):
        self.param.smoother_halo_precision = value

    @property
    def smoother_schwarz_type(self):
        return self.param.smoother_schwarz_type

    @smoother_schwarz_type.setter
    def smoother_schwarz_type(self, value):
        self.param.smoother_schwarz_type = value

    @property
    def smoother_schwarz_cycle(self):
        return self.param.smoother_schwarz_cycle

    @smoother_schwarz_cycle.setter
    def smoother_schwarz_cycle(self, value):
        self.param.smoother_schwarz_cycle = value

    @property
    def coarse_grid_solution_type(self):
        return self.param.coarse_grid_solution_type

    @coarse_grid_solution_type.setter
    def coarse_grid_solution_type(self, value):
        self.param.coarse_grid_solution_type = value

    @property
    def smoother_solve_type(self):
        return self.param.smoother_solve_type

    @smoother_solve_type.setter
    def smoother_solve_type(self, value):
        self.param.smoother_solve_type = value

    @property
    def cycle_type(self):
        return self.param.cycle_type

    @cycle_type.setter
    def cycle_type(self, value):
        self.param.cycle_type = value

    @property
    def global_reduction(self):
        return self.param.global_reduction

    @global_reduction.setter
    def global_reduction(self, value):
        self.param.global_reduction = value

    @property
    def location(self):
        return self.param.location

    @location.setter
    def location(self, value):
        self.param.location = value

    @property
    def setup_location(self):
        return self.param.setup_location

    @setup_location.setter
    def setup_location(self, value):
        self.param.setup_location = value

    @property
    def use_eig_solver(self):
        return self.param.use_eig_solver

    @use_eig_solver.setter
    def use_eig_solver(self, value):
        self.param.use_eig_solver = value

    @property
    def compute_null_vector(self):
        return self.param.compute_null_vector

    @compute_null_vector.setter
    def compute_null_vector(self, value):
        self.param.compute_null_vector = value

    @property
    def generate_all_levels(self):
        return self.param.generate_all_levels

    @generate_all_levels.setter
    def generate_all_levels(self, value):
        self.param.generate_all_levels = value

    @property
    def run_verify(self):
        return self.param.run_verify

    @run_verify.setter
    def run_verify(self, value):
        self.param.run_verify = value

    @property
    def run_low_mode_check(self):
        return self.param.run_low_mode_check

    @run_low_mode_check.setter
    def run_low_mode_check(self, value):
        self.param.run_low_mode_check = value

    @property
    def run_oblique_proj_check(self):
        return self.param.run_oblique_proj_check

    @run_oblique_proj_check.setter
    def run_oblique_proj_check(self, value):
        self.param.run_oblique_proj_check = value

    @property
    def vec_load(self):
        return self.param.vec_load

    @vec_load.setter
    def vec_load(self, value):
        self.param.vec_load = value

    @property
    def vec_infile(self):
        value = []
        for i in range(self.n_level):
            value.append(self.param.vec_infile[i])
        return value

    @vec_infile.setter
    def vec_infile(self, value):
        for i in range(self.n_level):
            self.param.vec_infile[i] = value[i]

    @property
    def vec_store(self):
        return self.param.vec_store

    @vec_store.setter
    def vec_store(self, value):
        self.param.vec_store = value

    @property
    def vec_outfile(self):
        value = []
        for i in range(self.n_level):
            value.append(self.param.vec_outfile[i])
        return value

    @vec_outfile.setter
    def vec_outfile(self, value):
        for i in range(self.n_level):
            self.param.vec_outfile[i] = value[i]

    @property
    def mg_vec_partfile(self):
        return self.param.mg_vec_partfile

    @mg_vec_partfile.setter
    def mg_vec_partfile(self, value):
        self.param.mg_vec_partfile = value

    @property
    def coarse_guess(self):
        return self.param.coarse_guess

    @coarse_guess.setter
    def coarse_guess(self, value):
        self.param.coarse_guess = value

    @property
    def preserve_deflation(self):
        return self.param.preserve_deflation

    @preserve_deflation.setter
    def preserve_deflation(self, value):
        self.param.preserve_deflation = value

    @property
    def mu_factor(self):
        return self.param.mu_factor

    @mu_factor.setter
    def mu_factor(self, value):
        self.param.mu_factor = value

    @property
    def transfer_type(self):
        return self.param.transfer_type

    @transfer_type.setter
    def transfer_type(self, value):
        self.param.transfer_type = value

    @property
    def allow_truncation(self):
        return self.param.allow_truncation

    @allow_truncation.setter
    def allow_truncation(self, value):
        self.param.allow_truncation = value

    @property
    def staggered_kd_dagger_approximation(self):
        return self.param.staggered_kd_dagger_approximation

    @staggered_kd_dagger_approximation.setter
    def staggered_kd_dagger_approximation(self, value):
        self.param.staggered_kd_dagger_approximation = value

    @property
    def thin_update_only(self):
        return self.param.thin_update_only

    @thin_update_only.setter
    def thin_update_only(self, value):
        self.param.thin_update_only = value

cdef class QudaEigParam:
    cdef quda.QudaEigParam param

    def __init__(self):
        self.param = quda.newQudaEigParam()

    def __repr__(self):
        value = bytearray()
        with redirect_stdout(value):
            quda.printQudaEigParam(&self.param)
        return value.decode(sys.stdout.encoding)

    cdef from_ptr(self, quda.QudaEigParam *ptr):
        self.param = dereference(ptr)

    @property
    def struct_size(self):
        return self.param.struct_size

    @struct_size.setter
    def struct_size(self, value):
        self.param.struct_size = value

    @property
    def invert_param(self):
        param = QudaInvertParam()
        param.from_ptr(self.param.invert_param)
        return param

    @invert_param.setter
    def invert_param(self, value):
        self.set_invert_param(value)

    cdef set_invert_param(self, QudaInvertParam value):
        self.param.invert_param = &value.param

    @property
    def eig_type(self):
        return self.param.eig_type

    @eig_type.setter
    def eig_type(self, value):
        self.param.eig_type = value

    @property
    def use_poly_acc(self):
        return self.param.use_poly_acc

    @use_poly_acc.setter
    def use_poly_acc(self, value):
        self.param.use_poly_acc = value

    @property
    def poly_deg(self):
        return self.param.poly_deg

    @poly_deg.setter
    def poly_deg(self, value):
        self.param.poly_deg = value

    @property
    def a_min(self):
        return self.param.a_min

    @a_min.setter
    def a_min(self, value):
        self.param.a_min = value

    @property
    def a_max(self):
        return self.param.a_max

    @a_max.setter
    def a_max(self, value):
        self.param.a_max = value

    @property
    def preserve_deflation(self):
        return self.param.preserve_deflation

    @preserve_deflation.setter
    def preserve_deflation(self, value):
        self.param.preserve_deflation = value

    @property
    def preserve_deflation_space(self):
        ptr = Pointer("void")
        ptr.set_ptr(self.param.preserve_deflation_space)
        return ptr

    @preserve_deflation_space.setter
    def preserve_deflation_space(self, Pointer value):
        assert value.dtype == "void"
        self.param.preserve_deflation_space = value.ptr

    @property
    def preserve_evals(self):
        return self.param.preserve_evals

    @preserve_evals.setter
    def preserve_evals(self, value):
        self.param.preserve_evals = value

    @property
    def use_smeared_gauge(self):
        return self.param.use_smeared_gauge

    @use_smeared_gauge.setter
    def use_smeared_gauge(self, value):
        self.param.use_smeared_gauge = value

    @property
    def use_dagger(self):
        return self.param.use_dagger

    @use_dagger.setter
    def use_dagger(self, value):
        self.param.use_dagger = value

    @property
    def use_norm_op(self):
        return self.param.use_norm_op

    @use_norm_op.setter
    def use_norm_op(self, value):
        self.param.use_norm_op = value

    @property
    def use_pc(self):
        return self.param.use_pc

    @use_pc.setter
    def use_pc(self, value):
        self.param.use_pc = value

    @property
    def use_eigen_qr(self):
        return self.param.use_eigen_qr

    @use_eigen_qr.setter
    def use_eigen_qr(self, value):
        self.param.use_eigen_qr = value

    @property
    def compute_svd(self):
        return self.param.compute_svd

    @compute_svd.setter
    def compute_svd(self, value):
        self.param.compute_svd = value

    @property
    def compute_gamma5(self):
        return self.param.compute_gamma5

    @compute_gamma5.setter
    def compute_gamma5(self, value):
        self.param.compute_gamma5 = value

    @property
    def require_convergence(self):
        return self.param.require_convergence

    @require_convergence.setter
    def require_convergence(self, value):
        self.param.require_convergence = value

    @property
    def spectrum(self):
        return self.param.spectrum

    @spectrum.setter
    def spectrum(self, value):
        self.param.spectrum = value

    @property
    def n_ev(self):
        return self.param.n_ev

    @n_ev.setter
    def n_ev(self, value):
        self.param.n_ev = value

    @property
    def n_kr(self):
        return self.param.n_kr

    @n_kr.setter
    def n_kr(self, value):
        self.param.n_kr = value

    @property
    def nLockedMax(self):
        return self.param.nLockedMax

    @nLockedMax.setter
    def nLockedMax(self, value):
        self.param.nLockedMax = value

    @property
    def n_conv(self):
        return self.param.n_conv

    @n_conv.setter
    def n_conv(self, value):
        self.param.n_conv = value

    @property
    def n_ev_deflate(self):
        return self.param.n_ev_deflate

    @n_ev_deflate.setter
    def n_ev_deflate(self, value):
        self.param.n_ev_deflate = value

    @property
    def tol(self):
        return self.param.tol

    @tol.setter
    def tol(self, value):
        self.param.tol = value

    @property
    def qr_tol(self):
        return self.param.qr_tol

    @qr_tol.setter
    def qr_tol(self, value):
        self.param.qr_tol = value

    @property
    def check_interval(self):
        return self.param.check_interval

    @check_interval.setter
    def check_interval(self, value):
        self.param.check_interval = value

    @property
    def max_restarts(self):
        return self.param.max_restarts

    @max_restarts.setter
    def max_restarts(self, value):
        self.param.max_restarts = value

    @property
    def batched_rotate(self):
        return self.param.batched_rotate

    @batched_rotate.setter
    def batched_rotate(self, value):
        self.param.batched_rotate = value

    @property
    def block_size(self):
        return self.param.block_size

    @block_size.setter
    def block_size(self, value):
        self.param.block_size = value

    @property
    def compute_evals_batch_size(self):
        return self.param.compute_evals_batch_size

    @compute_evals_batch_size.setter
    def compute_evals_batch_size(self, value):
        self.param.compute_evals_batch_size = value

    @property
    def max_ortho_attempts(self):
        return self.param.max_ortho_attempts

    @max_ortho_attempts.setter
    def max_ortho_attempts(self, value):
        self.param.max_ortho_attempts = value

    @property
    def ortho_block_size(self):
        return self.param.ortho_block_size

    @ortho_block_size.setter
    def ortho_block_size(self, value):
        self.param.ortho_block_size = value

    @property
    def arpack_check(self):
        return self.param.arpack_check

    @arpack_check.setter
    def arpack_check(self, value):
        self.param.arpack_check = value

    @property
    def arpack_logfile(self):
        return self.param.arpack_logfile

    @arpack_logfile.setter
    def arpack_logfile(self, const char value[]):
        self.param.arpack_logfile = value

    @property
    def QUDA_logfile(self):
        return self.param.QUDA_logfile

    @QUDA_logfile.setter
    def QUDA_logfile(self, const char value[]):
        self.param.QUDA_logfile = value

    @property
    def ortho_dim(self):
        return self.param.ortho_dim

    @ortho_dim.setter
    def ortho_dim(self, value):
        self.param.ortho_dim = value

    @property
    def ortho_dim_size_local(self):
        return self.param.ortho_dim_size_local

    @ortho_dim_size_local.setter
    def ortho_dim_size_local(self, value):
        self.param.ortho_dim_size_local = value

    @property
    def nk(self):
        return self.param.nk

    @nk.setter
    def nk(self, value):
        self.param.nk = value

    @property
    def np(self):
        return self.param.np

    @np.setter
    def np(self, value):
        self.param.np = value

    @property
    def import_vectors(self):
        return self.param.import_vectors

    @import_vectors.setter
    def import_vectors(self, value):
        self.param.import_vectors = value

    @property
    def cuda_prec_ritz(self):
        return self.param.cuda_prec_ritz

    @cuda_prec_ritz.setter
    def cuda_prec_ritz(self, value):
        self.param.cuda_prec_ritz = value

    @property
    def mem_type_ritz(self):
        return self.param.mem_type_ritz

    @mem_type_ritz.setter
    def mem_type_ritz(self, value):
        self.param.mem_type_ritz = value

    @property
    def location(self):
        return self.param.location

    @location.setter
    def location(self, value):
        self.param.location = value

    @property
    def run_verify(self):
        return self.param.run_verify

    @run_verify.setter
    def run_verify(self, value):
        self.param.run_verify = value

    @property
    def vec_infile(self):
        return self.param.vec_infile

    @vec_infile.setter
    def vec_infile(self, const char value[]):
        self.param.vec_infile = value

    @property
    def vec_outfile(self):
        return self.param.vec_outfile

    @vec_outfile.setter
    def vec_outfile(self, const char value[]):
        self.param.vec_outfile = value

    @property
    def save_prec(self):
        return self.param.save_prec

    @save_prec.setter
    def save_prec(self, value):
        self.param.save_prec = value

    @property
    def io_parity_inflate(self):
        return self.param.io_parity_inflate

    @io_parity_inflate.setter
    def io_parity_inflate(self, value):
        self.param.io_parity_inflate = value

    @property
    def partfile(self):
        return self.param.partfile

    @partfile.setter
    def partfile(self, value):
        self.param.partfile = value

    @property
    def extlib_type(self):
        return self.param.extlib_type

    @extlib_type.setter
    def extlib_type(self, value):
        self.param.extlib_type = value

cdef class QudaGaugeObservableParam:
    cdef quda.QudaGaugeObservableParam param

    def __init__(self):
        self.param = quda.newQudaGaugeObservableParam()

    def __repr__(self):
        value = bytearray()
        with redirect_stdout(value):
            quda.printQudaGaugeObservableParam(&self.param)
        return value.decode(sys.stdout.encoding)

    cdef from_ptr(self, quda.QudaGaugeObservableParam *ptr):
        self.param = dereference(ptr)

    @property
    def struct_size(self):
        return self.param.struct_size

    @struct_size.setter
    def struct_size(self, value):
        self.param.struct_size = value

    @property
    def su_project(self):
        return self.param.su_project

    @su_project.setter
    def su_project(self, value):
        self.param.su_project = value

    @property
    def compute_plaquette(self):
        return self.param.compute_plaquette

    @compute_plaquette.setter
    def compute_plaquette(self, value):
        self.param.compute_plaquette = value

    @property
    def plaquette(self):
        return self.param.plaquette

    @plaquette.setter
    def plaquette(self, value):
        self.param.plaquette = value

    @property
    def compute_rectangle(self):
        return self.param.compute_rectangle

    @compute_rectangle.setter
    def compute_rectangle(self, value):
        self.param.compute_rectangle = value

    @property
    def rectangle(self):
        return self.param.rectangle

    @rectangle.setter
    def rectangle(self, value):
        self.param.rectangle = value

    @property
    def compute_polyakov_loop(self):
        return self.param.compute_polyakov_loop

    @compute_polyakov_loop.setter
    def compute_polyakov_loop(self, value):
        self.param.compute_polyakov_loop = value

    @property
    def ploop(self):
        return self.param.ploop

    @ploop.setter
    def ploop(self, value):
        self.param.ploop = value

    @property
    def compute_gauge_loop_trace(self):
        return self.param.compute_gauge_loop_trace

    @compute_gauge_loop_trace.setter
    def compute_gauge_loop_trace(self, value):
        self.param.compute_gauge_loop_trace = value

    @property
    def traces(self):
        ptr = Pointer("double_complex")
        ptr.set_ptr(<void *>self.param.traces)
        return ptr

    @traces.setter
    def traces(self, Pointer value):
        assert value.dtype == "double_complex"
        self.param.traces = <double_complex *>value.ptr

    @property
    def input_path_buff(self):
        ptrs = Pointers("int", 0)
        ptrs.set_ptrs(<void **>self.param.input_path_buff)
        return ptrs

    @input_path_buff.setter
    def input_path_buff(self, Pointers value):
        assert value.dtype == "int"
        self.param.input_path_buff = <int **>value.ptrs

    @property
    def path_length(self):
        ptr = Pointer("int")
        ptr.set_ptr(<void *>self.param.path_length)
        return ptr

    @path_length.setter
    def path_length(self, Pointer value):
        assert value.dtype == "int"
        self.param.path_length = <int *>value.ptr

    @property
    def loop_coeff(self):
        ptr = Pointer("double")
        ptr.set_ptr(<void *>self.param.loop_coeff)
        return ptr

    @loop_coeff.setter
    def loop_coeff(self, Pointer value):
        assert value.dtype == "double"
        self.param.loop_coeff = <double *>value.ptr

    @property
    def num_paths(self):
        return self.param.num_paths

    @num_paths.setter
    def num_paths(self, value):
        self.param.num_paths = value

    @property
    def max_length(self):
        return self.param.max_length

    @max_length.setter
    def max_length(self, value):
        self.param.max_length = value

    @property
    def factor(self):
        return self.param.factor

    @factor.setter
    def factor(self, value):
        self.param.factor = value

    @property
    def compute_qcharge(self):
        return self.param.compute_qcharge

    @compute_qcharge.setter
    def compute_qcharge(self, value):
        self.param.compute_qcharge = value

    @property
    def qcharge(self):
        return self.param.qcharge

    @qcharge.setter
    def qcharge(self, value):
        self.param.qcharge = value

    @property
    def energy(self):
        return self.param.energy

    @energy.setter
    def energy(self, value):
        self.param.energy = value

    @property
    def compute_qcharge_density(self):
        return self.param.compute_qcharge_density

    @compute_qcharge_density.setter
    def compute_qcharge_density(self, value):
        self.param.compute_qcharge_density = value

    @property
    def qcharge_density(self):
        ptr = Pointer("void")
        ptr.set_ptr(self.param.qcharge_density)
        return ptr

    @qcharge_density.setter
    def qcharge_density(self, Pointer value):
        assert value.dtype == "void"
        self.param.qcharge_density = value.ptr

    @property
    def remove_staggered_phase(self):
        return self.param.remove_staggered_phase

    @remove_staggered_phase.setter
    def remove_staggered_phase(self, value):
        self.param.remove_staggered_phase = value

cdef class QudaGaugeSmearParam:
    cdef quda.QudaGaugeSmearParam param

    def __init__(self):
        self.param = quda.newQudaGaugeSmearParam()

    # def __repr__(self):
    #     value = bytearray()
    #     with redirect_stdout(value):
    #         quda.printQudaGaugeSmearParam(&self.param)
    #     return value.decode(sys.stdout.encoding)

    cdef from_ptr(self, quda.QudaGaugeSmearParam *ptr):
        self.param = dereference(ptr)

    @property
    def struct_size(self):
        return self.param.struct_size

    @struct_size.setter
    def struct_size(self, value):
        self.param.struct_size = value

    @property
    def n_steps(self):
        return self.param.n_steps

    @n_steps.setter
    def n_steps(self, value):
        self.param.n_steps = value

    @property
    def epsilon(self):
        return self.param.epsilon

    @epsilon.setter
    def epsilon(self, value):
        self.param.epsilon = value

    @property
    def smear_anisotropy(self):
        return self.param.smear_anisotropy

    @smear_anisotropy.setter
    def smear_anisotropy(self, value):
        self.param.smear_anisotropy = value

    @property
    def rk_order(self):
        return self.param.rk_order

    @rk_order.setter
    def rk_order(self, value):
        self.param.rk_order = value

    @property
    def alpha(self):
        return self.param.alpha

    @alpha.setter
    def alpha(self, value):
        self.param.alpha = value

    @property
    def rho(self):
        return self.param.rho

    @rho.setter
    def rho(self, value):
        self.param.rho = value

    @property
    def alpha1(self):
        return self.param.alpha1

    @alpha1.setter
    def alpha1(self, value):
        self.param.alpha1 = value

    @property
    def alpha2(self):
        return self.param.alpha2

    @alpha2.setter
    def alpha2(self, value):
        self.param.alpha2 = value

    @property
    def alpha3(self):
        return self.param.alpha3

    @alpha3.setter
    def alpha3(self, value):
        self.param.alpha3 = value

    @property
    def meas_interval(self):
        return self.param.meas_interval

    @meas_interval.setter
    def meas_interval(self, value):
        self.param.meas_interval = value

    @property
    def smear_type(self):
        return self.param.smear_type

    @smear_type.setter
    def smear_type(self, value):
        self.param.smear_type = value

    @property
    def adj_n_save(self):
        return self.param.adj_n_save

    @adj_n_save.setter
    def adj_n_save(self, value):
        self.param.adj_n_save = value

    @property
    def hier_threshold(self):
        return self.param.hier_threshold

    @hier_threshold.setter
    def hier_threshold(self, value):
        self.param.hier_threshold = value

    @property
    def restart(self):
        return self.param.restart

    @restart.setter
    def restart(self, value):
        self.param.restart = value

    @property
    def t0(self):
        return self.param.t0

    @t0.setter
    def t0(self, value):
        self.param.t0 = value

    @property
    def dir_ignore(self):
        return self.param.dir_ignore

    @dir_ignore.setter
    def dir_ignore(self, value):
        self.param.dir_ignore = value

cdef class QudaBLASParam:
    cdef quda.QudaBLASParam param

    def __init__(self):
        self.param = quda.newQudaBLASParam()

    def __repr__(self):
        value = bytearray()
        with redirect_stdout(value):
            quda.printQudaBLASParam(&self.param)
        return value.decode(sys.stdout.encoding)

    cdef from_ptr(self, quda.QudaBLASParam *ptr):
        self.param = dereference(ptr)

    @property
    def struct_size(self):
        return self.param.struct_size

    @struct_size.setter
    def struct_size(self, value):
        self.param.struct_size = value

    @property
    def blas_type(self):
        return self.param.blas_type

    @blas_type.setter
    def blas_type(self, value):
        self.param.blas_type = value

    @property
    def trans_a(self):
        return self.param.trans_a

    @trans_a.setter
    def trans_a(self, value):
        self.param.trans_a = value

    @property
    def trans_b(self):
        return self.param.trans_b

    @trans_b.setter
    def trans_b(self, value):
        self.param.trans_b = value

    @property
    def m(self):
        return self.param.m

    @m.setter
    def m(self, value):
        self.param.m = value

    @property
    def n(self):
        return self.param.n

    @n.setter
    def n(self, value):
        self.param.n = value

    @property
    def k(self):
        return self.param.k

    @k.setter
    def k(self, value):
        self.param.k = value

    @property
    def lda(self):
        return self.param.lda

    @lda.setter
    def lda(self, value):
        self.param.lda = value

    @property
    def ldb(self):
        return self.param.ldb

    @ldb.setter
    def ldb(self, value):
        self.param.ldb = value

    @property
    def ldc(self):
        return self.param.ldc

    @ldc.setter
    def ldc(self, value):
        self.param.ldc = value

    @property
    def a_offset(self):
        return self.param.a_offset

    @a_offset.setter
    def a_offset(self, value):
        self.param.a_offset = value

    @property
    def b_offset(self):
        return self.param.b_offset

    @b_offset.setter
    def b_offset(self, value):
        self.param.b_offset = value

    @property
    def c_offset(self):
        return self.param.c_offset

    @c_offset.setter
    def c_offset(self, value):
        self.param.c_offset = value

    @property
    def a_stride(self):
        return self.param.a_stride

    @a_stride.setter
    def a_stride(self, value):
        self.param.a_stride = value

    @property
    def b_stride(self):
        return self.param.b_stride

    @b_stride.setter
    def b_stride(self, value):
        self.param.b_stride = value

    @property
    def c_stride(self):
        return self.param.c_stride

    @c_stride.setter
    def c_stride(self, value):
        self.param.c_stride = value

    @property
    def alpha(self):
        return self.param.alpha

    @alpha.setter
    def alpha(self, value):
        self.param.alpha = value

    @property
    def beta(self):
        return self.param.beta

    @beta.setter
    def beta(self, value):
        self.param.beta = value

    @property
    def inv_mat_size(self):
        return self.param.inv_mat_size

    @inv_mat_size.setter
    def inv_mat_size(self, value):
        self.param.inv_mat_size = value

    @property
    def batch_count(self):
        return self.param.batch_count

    @batch_count.setter
    def batch_count(self, value):
        self.param.batch_count = value

    @property
    def data_type(self):
        return self.param.data_type

    @data_type.setter
    def data_type(self, value):
        self.param.data_type = value

    @property
    def data_order(self):
        return self.param.data_order

    @data_order.setter
    def data_order(self, value):
        self.param.data_order = value

def setVerbosityQuda(quda.QudaVerbosity verbosity, const char prefix[]):
    quda.setVerbosityQuda(verbosity, prefix, stdout)

ctypedef struct MapData:
    int ndim
    int dims[6]

cdef MapData map_data

cdef int defaultMap(const int *coords, void *fdata) noexcept:
    cdef MapData *md = <MapData *>fdata
    cdef int rank = 0
    for i in range(md.ndim):
        rank = rank * md.dims[i] + coords[i]
    return rank

cdef int reversedMap(const int *coords, void *fdata) noexcept:
    cdef MapData *md = <MapData *>fdata
    cdef int rank = coords[md.ndim - 1]
    for i in range(md.ndim - 2, -1, -1):
        rank = rank * md.dims[i] + coords[i]
    return rank

def _defaultRankFromCoord(coords: Sequence[int], dims: Sequence[int]) -> int:
    rank = 0
    for coord, dim in zip(coords, dims):
        rank = rank * dim + coord
    return rank


def _defaultCoordFromRank(rank: int, dims: Sequence[int]) -> List[int]:
    coords = []
    for dim in dims[::-1]:
        coords.append(rank % dim)
        rank = rank // dim
    return coords[::-1]

shared_rank_list: list = None

cdef int sharedMap(const int *coords, void *fdata) noexcept:
    cdef MapData *md = <MapData *>fdata
    global shared_rank_list
    grid_size = [md.dims[i] for i in range(md.ndim)]
    if shared_rank_list is None:
        comm = MPI.COMM_WORLD
        shared_comm = comm.Split_type(MPI.COMM_TYPE_SHARED)
        shared_size = shared_comm.Get_size()
        shared_rank = shared_comm.Get_rank()
        shared_root = shared_comm.bcast(comm.Get_rank())
        node_rank = comm.allgather(shared_root).index(shared_root)
        node_grid_size = [G for G in grid_size]
        shared_grid_size = [1 for _ in grid_size]
        dim, last_dim = 0, len(grid_size) - 1
        while shared_size > 1:
            for prime in [2, 3, 5]:
                if node_grid_size[dim] % prime == 0 and shared_size % prime == 0:
                    node_grid_size[dim] //= prime
                    shared_grid_size[dim] *= prime
                    shared_size //= prime
                    last_dim = dim
                    break
            else:
                if last_dim == dim:
                    raise ValueError("GlobalSharedMemory::GetShmDims failed")
            dim = (dim + 1) % len(grid_size)
        grid_coord = [
            n * S + s
            for n, S, s in zip(
                _defaultCoordFromRank(node_rank, node_grid_size),
                shared_grid_size,
                _defaultCoordFromRank(shared_rank, shared_grid_size),
            )
        ]
        shared_rank_list = comm.allgather(_defaultRankFromCoord(grid_coord, grid_size))

    cdef int rank = shared_rank_list.index(defaultMap(coords, fdata))
    return rank

def initCommsGridQuda(int nDim, list dims, const char grid_map[]):
    cdef int _dims[4]
    _dims = dims
    map_data.ndim = nDim
    for i in range(nDim):
        map_data.dims[i] = _dims[i]
    if strcmp(grid_map, "default") == 0:
        quda.initCommsGridQuda(nDim, _dims, NULL, NULL)
    elif strcmp(grid_map, "reversed") == 0:
        quda.initCommsGridQuda(nDim, _dims, reversedMap, <void *>(&map_data))
    elif strcmp(grid_map, "shared") == 0:
        quda.initCommsGridQuda(nDim, _dims, sharedMap, <void *>(&map_data))

def initQudaDevice(int device):
    quda.initQudaDevice(device)

def initQudaMemory():
    quda.initQudaMemory()

def initQuda(int device):
    quda.initQuda(device)

def endQuda():
    quda.endQuda()

def updateR():
    quda.updateR()

def loadGaugeQuda(h_gauge, QudaGaugeParam param):
    _h_gauge = _NDArray(h_gauge, 2)
    quda.loadGaugeQuda(_h_gauge.ptr, &param.param)

def freeGaugeQuda():
    quda.freeGaugeQuda()

def freeUniqueGaugeQuda(quda.QudaLinkType link_type):
    quda.freeUniqueGaugeQuda(link_type)

def freeGaugeSmearedQuda():
    quda.freeGaugeSmearedQuda()

def saveGaugeQuda(h_gauge, QudaGaugeParam param):
    _h_gauge = _NDArray(h_gauge, 2)
    quda.saveGaugeQuda(_h_gauge.ptr, &param.param)

def loadCloverQuda(h_clover, h_clovinv, QudaInvertParam inv_param):
    _h_clover = _NDArray(h_clover, 1)
    _h_clovinv = _NDArray(h_clovinv, 1)
    quda.loadCloverQuda(_h_clover.ptr, _h_clovinv.ptr, &inv_param.param)

def freeCloverQuda():
    quda.freeCloverQuda()

# QUDA only declares lanczosQuda
# def lanczosQuda(int k0, int m, Pointer hp_Apsi, Pointer hp_r, Pointer hp_V, Pointer hp_alpha, Pointer hp_beta, QudaEigParam eig_param):

def eigensolveQuda(h_evecs, ndarray[double_complex, ndim=1] h_evals, QudaEigParam param):
    _h_evecs = _NDArray(h_evecs, 2)
    _h_evals = _NDArray(h_evals)
    quda.eigensolveQuda(_h_evecs.ptrs, <double_complex *>_h_evals.ptr, &param.param)

def invertQuda(h_x, h_b, QudaInvertParam param):
    _h_x = _NDArray(h_x, 1)
    _h_b = _NDArray(h_b, 1)
    quda.invertQuda(_h_x.ptr, _h_b.ptr, &param.param)

def invertMultiSrcQuda(_hp_x, _hp_b, QudaInvertParam param):
    __hp_x = _NDArray(_hp_x, 2)
    __hp_b = _NDArray(_hp_b, 2)
    quda.invertMultiSrcQuda(__hp_x.ptrs, __hp_b.ptrs, &param.param)

def invertMultiShiftQuda(_hp_x, _hp_b, QudaInvertParam param):
    __hp_x = _NDArray(_hp_x, 2)
    __hp_b = _NDArray(_hp_b, 1)
    quda.invertMultiShiftQuda(__hp_x.ptrs, __hp_b.ptr, &param.param)

def newMultigridQuda(QudaMultigridParam param):
    mg_instance = Pointer("void")
    mg_instance.set_ptr(quda.newMultigridQuda(&param.param))
    return mg_instance

def destroyMultigridQuda(Pointer mg_instance):
    quda.destroyMultigridQuda(mg_instance.ptr)

def updateMultigridQuda(Pointer mg_instance, QudaMultigridParam param):
    quda.updateMultigridQuda(mg_instance.ptr, &param.param)

def dumpMultigridQuda(Pointer mg_instance, QudaMultigridParam param):
    quda.dumpMultigridQuda(mg_instance.ptr, &param.param)

def dslashQuda(h_out, h_in, QudaInvertParam inv_param, quda.QudaParity parity):
    _h_out = _NDArray(h_out, 1)
    _h_in = _NDArray(h_in, 1)
    quda.dslashQuda(_h_out.ptr, _h_in.ptr, &inv_param.param, parity)

def dslashMultiSrcQuda(_hp_x, _hp_b, QudaInvertParam param, quda.QudaParity parity):
    __hp_x = _NDArray(_hp_x, 2)
    __hp_b = _NDArray(_hp_b, 2)
    quda.dslashMultiSrcQuda(__hp_x.ptrs, __hp_b.ptrs, &param.param, parity)

def cloverQuda(h_out, h_in, QudaInvertParam inv_param, quda.QudaParity parity, int inverse):
    _h_out = _NDArray(h_out, 1)
    _h_in = _NDArray(h_in, 1)
    quda.cloverQuda(_h_out.ptr, _h_in.ptr, &inv_param.param, parity, inverse)

def MatQuda(h_out, h_in, QudaInvertParam inv_param):
    _h_out = _NDArray(h_out, 1)
    _h_in = _NDArray(h_in, 1)
    quda.MatQuda(_h_out.ptr, _h_in.ptr, &inv_param.param)

def MatDagMatQuda(h_out, h_in, QudaInvertParam inv_param):
    _h_out = _NDArray(h_out, 1)
    _h_in = _NDArray(h_in, 1)
    quda.MatDagMatQuda(_h_out.ptr, _h_in.ptr, &inv_param.param)

# void set_dim(int *)
# void pack_ghost(void **cpuLink, void **cpuGhost, int nFace, QudaPrecision precision)

def computeKSLinkQuda(fatlink, longlink, ulink, inlink, ndarray[double, ndim=1] path_coeff, QudaGaugeParam param):
    _fatlink = _NDArray(fatlink, 2)
    _longlink = _NDArray(longlink, 2)
    _ulink = _NDArray(ulink, 2)
    _inlink = _NDArray(inlink, 2)
    _path_coeff = _NDArray(path_coeff)
    quda.computeKSLinkQuda(_fatlink.ptr, _longlink.ptr, _ulink.ptr, _inlink.ptr, <double *>_path_coeff.ptr, &param.param)

def computeTwoLinkQuda(twolink, inlink, QudaGaugeParam param):
    _twolink = _NDArray(twolink, 2)
    _inlink = _NDArray(inlink, 2)
    quda.computeTwoLinkQuda(_twolink.ptr, _inlink.ptr, &param.param)

def momResidentQuda(mom, QudaGaugeParam param):
    _mom = _NDArray(mom, 2)
    quda.momResidentQuda(_mom.ptr, &param.param)

def computeGaugeForceQuda(mom, sitelink, ndarray[int, ndim=3] input_path_buf, ndarray[int, ndim=1] path_length, ndarray[double, ndim=1] loop_coeff, int num_paths, int max_length, double dt, QudaGaugeParam qudaGaugeParam):
    _mom = _NDArray(mom, 2)
    _sitelink = _NDArray(sitelink, 2)
    _input_path_buf = _NDArray(input_path_buf)
    _path_length = _NDArray(path_length)
    _loop_coeff = _NDArray(loop_coeff)
    return quda.computeGaugeForceQuda(_mom.ptr, _sitelink.ptr, <int ***>_input_path_buf.ptrss, <int *>_path_length.ptr, <double *>_loop_coeff.ptr, num_paths, max_length, dt, &qudaGaugeParam.param)

def computeGaugePathQuda(out, sitelink, ndarray[int, ndim=3] input_path_buf, ndarray[int, ndim=1] path_length, ndarray[double, ndim=1] loop_coeff, int num_paths, int max_length, double dt, QudaGaugeParam qudaGaugeParam):
    _out = _NDArray(out, 2)
    _sitelink = _NDArray(sitelink, 2)
    _input_path_buf = _NDArray(input_path_buf)
    _path_length = _NDArray(path_length)
    _loop_coeff = _NDArray(loop_coeff)
    return quda.computeGaugePathQuda(_out.ptr, _sitelink.ptr, <int ***>_input_path_buf.ptrss, <int *>_path_length.ptr, <double *>_loop_coeff.ptr, num_paths, max_length, dt, &qudaGaugeParam.param)

def computeGaugeLoopTraceQuda(ndarray[double_complex, ndim=1] traces, ndarray[int, ndim=2] input_path_buf, ndarray[int, ndim=1] path_length, ndarray[double, ndim=1] loop_coeff, int num_paths, int max_length, double factor):
    _traces = _NDArray(traces)
    _input_path_buf = _NDArray(input_path_buf)
    _path_length = _NDArray(path_length)
    _loop_coeff = _NDArray(loop_coeff)
    quda.computeGaugeLoopTraceQuda(<double_complex *>_traces.ptr, <int **>_input_path_buf.ptrs, <int *>_path_length.ptr, <double *>_loop_coeff.ptr, num_paths, max_length, factor)

def updateGaugeFieldQuda(gauge, momentum, double dt, int conj_mom, int exact, QudaGaugeParam param):
    _gauge = _NDArray(gauge, 2)
    _momentum = _NDArray(momentum, 2)
    quda.updateGaugeFieldQuda(_gauge.ptr, _momentum.ptr, dt, conj_mom, exact, &param.param)

def staggeredPhaseQuda(gauge_h, QudaGaugeParam param):
    _gauge_h = _NDArray(gauge_h, 2)
    quda.staggeredPhaseQuda(_gauge_h.ptr, &param.param)

def projectSU3Quda(gauge_h, double tol, QudaGaugeParam param):
    _gauge_h = _NDArray(gauge_h, 2)
    quda.projectSU3Quda(_gauge_h.ptr, tol, &param.param)

def momActionQuda(momentum, QudaGaugeParam param):
    _momentum = _NDArray(momentum, 2)
    return quda.momActionQuda(_momentum.ptr, &param.param)

# void* createGaugeFieldQuda(void* gauge, int geometry, QudaGaugeParam* param)
# void saveGaugeFieldQuda(void* outGauge, void* inGauge, QudaGaugeParam* param)
# void destroyGaugeFieldQuda(void* gauge)

def createCloverQuda(QudaInvertParam param):
    quda.createCloverQuda(&param.param)

def computeCloverForceQuda(mom, double dt, x, ndarray[double, ndim=1] coeff, double kappa2, double ck, int nvector, double multiplicity, QudaGaugeParam gauge_param, QudaInvertParam inv_param):
    _mom = _NDArray(mom, 2)
    _x = _NDArray(x, 2)
    _coeff = _NDArray(coeff)
    quda.computeCloverForceQuda(_mom.ptr, dt, _x.ptrs, NULL, <double *>_coeff.ptr, kappa2, ck, nvector, multiplicity, NULL, &gauge_param.param, &inv_param.param)

# void computeStaggeredForceQuda(void *mom, double dt, double delta, void *gauge, void **x, QudaGaugeParam *gauge_param, QudaInvertParam *invert_param)

def computeHISQForceQuda(momentum, double dt, ndarray[double, ndim=1] level2_coeff, ndarray[double, ndim=1] fat7_coeff, w_link, v_link, u_link, quark, int num, int num_naik, ndarray[double, ndim=2] coeff, QudaGaugeParam param):
    _momentum = _NDArray(momentum, 2)
    _level2_coeff = _NDArray(level2_coeff)
    _fat7_coeff = _NDArray(fat7_coeff)
    _w_link = _NDArray(w_link, 2)
    _v_link = _NDArray(v_link, 2)
    _u_link = _NDArray(u_link, 2)
    _quark = _NDArray(quark, 2)
    _coeff = _NDArray(coeff)
    quda.computeHISQForceQuda(_momentum.ptr, dt, <double *>_level2_coeff.ptr, <double *>_fat7_coeff.ptr, _w_link.ptr, _v_link.ptr, _u_link.ptr, _quark.ptrs, num, num_naik, <double **>_coeff.ptrs, &param.param)

def gaussGaugeQuda(unsigned long long seed, double sigma):
    quda.gaussGaugeQuda(seed, sigma)

def gaussMomQuda(unsigned long long seed, double sigma):
    quda.gaussMomQuda(seed, sigma)

def plaqQuda():
    cdef double[3] plaq
    quda.plaqQuda(plaq)
    return plaq

def polyakovLoopQuda(int dir):
    cdef double[2] ploop
    quda.polyakovLoopQuda(ploop, dir)
    return ploop

# void copyExtendedResidentGaugeQuda(void *resident_gauge)

def performWuppertalnStep(h_out, h_in, QudaInvertParam param, unsigned int n_steps, double alpha):
    _h_out = _NDArray(h_out, 1)
    _h_in = _NDArray(h_in, 1)
    quda.performWuppertalnStep(_h_out.ptr, _h_in.ptr, &param.param, n_steps, alpha)

def performGaugeSmearQuda(QudaGaugeSmearParam smear_param, QudaGaugeObservableParam obs_param):
    quda.performGaugeSmearQuda(&smear_param.param, &obs_param.param)

def performWFlowQuda(QudaGaugeSmearParam smear_param, QudaGaugeObservableParam obs_param):
    quda.performWFlowQuda(&smear_param.param, &obs_param.param)

def gaugeObservablesQuda(QudaGaugeObservableParam param):
    quda.gaugeObservablesQuda(&param.param)

def contractQuda(x, y, result, quda.QudaContractType cType, QudaInvertParam param, ndarray[int, ndim=1] X):
    _x = _NDArray(x, 1)
    _y = _NDArray(y, 1)
    _result = _NDArray(result, 1)
    _X = _NDArray(X)
    quda.contractQuda(_x.ptr, _y.ptr, _result.ptr, cType, &param.param, <int *>_X.ptr)

def computeGaugeFixingOVRQuda(gauge, unsigned int gauge_dir, unsigned int Nsteps, unsigned int verbose_interval, double relax_boost, double tolerance, unsigned int reunit_interval, unsigned int stopWtheta, QudaGaugeParam param):
    _gauge = _NDArray(gauge, 2)
    return quda.computeGaugeFixingOVRQuda(_gauge.ptr, gauge_dir, Nsteps, verbose_interval, relax_boost, tolerance, reunit_interval, stopWtheta, &param.param)

def computeGaugeFixingFFTQuda(gauge, unsigned int gauge_dir, unsigned int Nsteps, unsigned int verbose_interval, double alpha, unsigned int autotune, double tolerance, unsigned int stopWtheta, QudaGaugeParam param):
    _gauge = _NDArray(gauge, 2)
    return quda.computeGaugeFixingFFTQuda(_gauge.ptr, gauge_dir, Nsteps, verbose_interval, alpha, autotune, tolerance, stopWtheta, &param.param)

def blasGEMMQuda(arrayA, arrayB, arrayC, quda.QudaBoolean native, QudaBLASParam param):
    _arrayA = _NDArray(arrayA, 1)
    _arrayB = _NDArray(arrayB, 1)
    _arrayC = _NDArray(arrayC, 1)
    quda.blasGEMMQuda(_arrayA.ptr, _arrayB.ptr, _arrayC.ptr, native, &param.param)

def blasLUInvQuda(Ainv, A, quda.QudaBoolean use_native, QudaBLASParam param):
    _Ainv = _NDArray(Ainv, 1)
    _A = _NDArray(A, 1)
    quda.blasLUInvQuda(_Ainv.ptr, _A.ptr, use_native, &param.param)

def flushChronoQuda(int index):
    quda.flushChronoQuda(index)

def newDeflationQuda(QudaEigParam param):
    df_instance = Pointer("void")
    df_instance.set_ptr(quda.newDeflationQuda(&param.param))
    return df_instance

def destroyDeflationQuda(Pointer df_instance):
    quda.destroyDeflationQuda(df_instance.ptr)

cdef class QudaQuarkSmearParam:
    cdef quda.QudaQuarkSmearParam param

    def __init__(self):
        # self.param = quda.QudaQuarkSmearParam()
        pass

    # def __repr__(self):
    #     value = bytearray()
    #     with redirect_stdout(value):
    #         quda.printQudaQuarkSmearParam(&self.param)
    #     return value.decode(sys.stdout.encoding)

    cdef from_ptr(self, quda.QudaQuarkSmearParam *ptr):
        self.param = dereference(ptr)

    @property
    def inv_param(self):
        param = QudaInvertParam()
        param.from_ptr(self.param.inv_param)
        return param

    @inv_param.setter
    def inv_param(self, value):
        self.set_inv_param(value)

    cdef set_inv_param(self, QudaInvertParam value):
        self.param.inv_param = &value.param

    @property
    def n_steps(self):
        return self.param.n_steps

    @n_steps.setter
    def n_steps(self, value):
        self.param.n_steps = value

    @property
    def width(self):
        return self.param.width

    @width.setter
    def width(self, value):
        self.param.width = value

    @property
    def compute_2link(self):
        return self.param.compute_2link

    @compute_2link.setter
    def compute_2link(self, value):
        self.param.compute_2link = value

    @property
    def delete_2link(self):
        return self.param.delete_2link

    @delete_2link.setter
    def delete_2link(self, value):
        self.param.delete_2link = value

    @property
    def t0(self):
        return self.param.t0

    @t0.setter
    def t0(self, value):
        self.param.t0 = value

    @property
    def secs(self):
        return self.param.secs

    @secs.setter
    def secs(self, value):
        self.param.secs = value

    @property
    def gflops(self):
        return self.param.gflops

    @gflops.setter
    def gflops(self, value):
        self.param.gflops = value

    @property
    def energy(self):
        return self.param.energy

    @energy.setter
    def energy(self, value):
        self.param.energy = value

    @property
    def power(self):
        return self.param.power

    @power.setter
    def power(self, value):
        self.param.power = value

    @property
    def temp(self):
        return self.param.temp

    @temp.setter
    def temp(self, value):
        self.param.temp = value

    @property
    def clock(self):
        return self.param.clock

    @clock.setter
    def clock(self, value):
        self.param.clock = value

def performTwoLinkGaussianSmearNStep(h_in, QudaQuarkSmearParam smear_param):
    _h_in = _NDArray(h_in, 1)
    quda.performTwoLinkGaussianSmearNStep(_h_in.ptr, &smear_param.param)
