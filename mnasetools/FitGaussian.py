import logging

import click
from lmfit.models import GaussianModel, ConstantModel

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import robtools.Split as sb
from robtools.txt import Parser


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--absolute/--relative', '-a/-r', default=False, show_default=True,
              help='Use absolute or relative number of reads')
@click.option('--components', '-c', is_flag=True,
              help='Shows fit components and initial fit in plot.')
@click.option('--svg', is_flag=True,
              help='Save vectorial plot.')
@click.option('--verbose', '-v', is_flag=True,
              help='Shows fit report.')
@click.option('--center', type=float, default=None,
              help='Center of gaussian. Defaults to 0')
@click.option('--cmin', '-cm', type=float, default=None,
              help='Minimum value for center of gaussian. Defaults to unbounded')
@click.option('--cmax', '-cM', type=float, default=None,
              help='Maximum value for center of gaussian. Defaults to unbounded')
@click.option('--amp', type=float, default=None,
              help='Amplitude of gaussian. Defaults to maximum relative frequency, approximately')
@click.option('--amin', '-am', type=float, default=None,
              help='Minimum amplitude of gaussian. Defaults to unbounded')
@click.option('--sigma', type=float, default=None,
              help='Width (sigma) of gaussian. Defaults to half of maximum index')
@click.option('--smin', '-sm', type=float, default=None,
              help='Minimum width (sigma) of gaussian. Defaults unbounded')
@click.option('--suffix', default=None,
              help='Suffix to append to sample name.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def fitgaussian(samples, absolute, components, svg, verbose, center, cmin, cmax, amp, amin, sigma, smin, suffix, index):
    '''Fits gaussian curve to dyad coverage.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fit_gaussian(samples, absolute, components, svg, verbose, center, cmin, cmax, amp, amin, sigma, smin, suffix, index)


def fit_gaussian(samples='samples.txt', absolute=False, components=False, svg=False, verbose=False, center=None, cmin=None, cmax=None, amp=None, amin=None, sigma=None, smin=None, suffix=None, index=None):
    '''Fits gaussian curve to dyad coverage.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        fit_gaussian_sample(sample, absolute, components, svg, verbose, center, cmin, cmax, amp, amin, sigma, smin, suffix)
        splits = sb.splits(sample)
        for split in splits:
            fit_gaussian_sample(split, absolute, components, svg, verbose, center, cmin, cmax, amp, amin, sigma, smin, suffix)


def fit_gaussian_sample(sample, absolute=False, components=False, svg=False, verbose=False, center=None, cmin=None, cmax=None, amp=None, amin=None, sigma=None, smin=None, suffix=None):
    '''Fits gaussian curve to dyad coverage for a single sample.'''
    print ('Fits gaussian curve to dyad coverage of sample {}'.format(sample))
    input = sample + (suffix if suffix else '') + '-dyad.txt'
    dyads = pd.read_csv(input, sep='\t', index_col=0, comment='#')
    x = dyads.index.values
    yheader = 'Frequency' if absolute else 'Relative Frequency'
    y = dyads[yheader].values
    if not amp:
        amp = dyads[yheader].max() * 100
    if not center:
        center = 0.0
    if not sigma:
        sigma = dyads.index.max() / 2
    plt.figure()
    plt.title(sample)
    plt.xlabel('Position relative to dyad (bp)')
    plt.ylabel('Frequency' if absolute else 'Relative Frequency')
    plt.xlim(x[0], x[len(x) - 1])
    plt.xticks(list(range(x[0], x[len(x) - 1] + 1, 25)))
    plt.plot(x, y, color='red')
    plot_output = sample + (suffix if suffix else '') + '-dyad-gaussian.png'
    try:
        constant = ConstantModel(prefix='c_')
        pars = constant.make_params()
        pars['c_c'].set(value=dyads[yheader].min(), min=0.0, max=dyads[yheader].max())
        gauss = GaussianModel(prefix='g_')
        pars.update(gauss.make_params())
        pars['g_center'].set(value=center, min=cmin, max=cmax)
        pars['g_sigma'].set(value=sigma, min=smin)
        pars['g_amplitude'].set(value=amp, min=amin)
        mod = constant + gauss
        init = mod.eval(pars, x=x)
        out = mod.fit(y, pars, x=x)
        if components:
            plt.plot(x, init, 'b--', label='Initial fit')
        if verbose:
            print(out.fit_report(min_correl=0.5))
        plt.plot(x, out.best_fit, 'b-', label='Best fit')
        if components:
            comps = out.eval_components(x=x)
            plt.plot(x, np.repeat(comps['c_'], len(x)), 'g--', label='Constant component')
            plt.plot(x, comps['g_'], 'm--', label='Gaussian component')
    except Exception as e:
        logging.warning('could not fit gaussian curve to sample {}'.format(sample), e)
    if components:
        plt.legend(loc='lower right')
    plt.savefig(plot_output)
    if svg:
        plot_svg_output = sample + (suffix if suffix else '') + '-dyad-gaussian.svg'
        plt.savefig(plot_svg_output, transparent=True)
    plt.close()


if __name__ == '__main__':
    fitgaussian()
