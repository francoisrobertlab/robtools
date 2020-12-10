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
@click.option('--gaussian', '-g', is_flag=True,
              help='Shows gaussian components scaled with the constant component.')
@click.option('--svg', is_flag=True,
              help='Save vectorial plot.')
@click.option('--verbose', '-v', is_flag=True,
              help='Shows fit report.')
@click.option('--center1', '-c1', type=float, default=None,
              help='Center of first gaussian. Defaults to minus a quater of maximum index')
@click.option('--cmin1', '-cm1', type=float, default=None,
              help='Minimum value for center of first gaussian. Defaults to unbounded')
@click.option('--cmax1', '-cM1', type=float, default=None,
              help='Maximum value for center of first gaussian. Defaults to unbounded')
@click.option('--amp1', '-a1', type=float, default=None,
              help='Amplitude of first gaussian. Defaults to half of maximum relative frequency, approximately')
@click.option('--amin1', '-am1', type=float, default=None,
              help='Minimum amplitude of first gaussian. Defaults to unbounded')
@click.option('--sigma1', '-s1', type=float, default=None,
              help='Width (sigma) of first gaussian. Defaults to a fifth of maximum index')
@click.option('--smin1', '-sm1', type=float, default=None,
              help='Minimum width (sigma) of first gaussian. Defaults unbounded')
@click.option('--center2', '-c2', type=float, default=None,
              help='Center of second gaussian. Defaults to plus a quater of maximum index')
@click.option('--cmin2', '-cm2', type=float, default=None,
              help='Minimum value for center of second gaussian. Defaults to unbounded')
@click.option('--cmax2', '-cM2', type=float, default=None,
              help='Maximum value for center of second gaussian. Defaults to unbounded')
@click.option('--amp2', '-a2', type=float, default=None,
              help='Amplitude of second gaussian. Defaults to half of maximum relative frequency, approximately')
@click.option('--amin2', '-am2', type=float, default=None,
              help='Minimum amplitude of second gaussian. Defaults to unbounded')
@click.option('--sigma2', '-s2', type=float, default=None,
              help='Width (sigma) of second gaussian. Defaults to a fifth of maximum index')
@click.option('--smin2', '-sm2', type=float, default=None,
              help='Minimum width (sigma) of second gaussian. Defaults to unbounded')
@click.option('--suffix', default=None,
              help='Suffix to append to sample name.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def fitdoublegaussian(samples, absolute, components, gaussian, svg, verbose, center1, cmin1, cmax1, amp1, amin1, sigma1, smin1, center2, cmin2, cmax2, amp2, amin2, sigma2, smin2, suffix, index):
    '''Fits double gaussian curve to dyad coverage.'''
    logging.basicConfig(filename='seqtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fit_double_gaussian(samples, absolute, components, gaussian, svg, verbose, center1, cmin1, cmax1, amp1, amin1, sigma1, smin1, center2, cmin2, cmax2, amp2, amin2, sigma2, smin2, suffix, index)


def fit_double_gaussian(samples='samples.txt', absolute=False, components=False, gaussian=False, svg=False, verbose=False, center1=None, cmin1=None, cmax1=None, amp1=None, amin1=None, sigma1=None, smin1=None, center2=None, cmin2=None, cmax2=None, amp2=None, amin2=None, sigma2=None, smin2=None, suffix=None, index=None):
    '''Fits double gaussian curve to dyad coverage.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        fit_double_gaussian_sample(sample, absolute, components, gaussian, svg, verbose, center1, cmin1, cmax1, amp1, amin1, sigma1, smin1, center2, cmin2, cmax2, amp2, amin2, sigma2, smin2, suffix)
        splits = sb.splits(sample)
        for split in splits:
            fit_double_gaussian_sample(split, absolute, components, gaussian, svg, verbose, center1, cmin1, cmax1, amp1, amin1, sigma1, smin1, center2, cmin2, cmax2, amp2, amin2, sigma2, smin2, suffix)
           

def fit_double_gaussian_sample(sample, absolute=False, components=False, gaussian=False, svg=False, verbose=False, center1=None, cmin1=None, cmax1=None, amp1=None, amin1=None, sigma1=None, smin1=None, center2=None, cmin2=None, cmax2=None, amp2=None, amin2=None, sigma2=None, smin2=None, suffix=None):
    '''Fits double gaussian curve to dyad coverage for a single sample.'''
    print ('Fits double gaussian curve to dyad coverage of sample {}'.format(sample))
    input = sample + (suffix if suffix else '') + '-dyad.txt'
    dyads = pd.read_csv(input, sep='\t', index_col=0, comment='#')
    x = dyads.index.values
    yheader = 'Frequency' if absolute else 'Relative Frequency'
    y = dyads[yheader].values
    if not amp1:
        amp1 = dyads[yheader].max() * 50
    if not center1:
        center1 = -dyads.index.max() / 4
    if not sigma1:
        sigma1 = dyads.index.max() / 5
    if not amp2:
        amp2 = dyads[yheader].max() * 50
    if not center2:
        center2 = dyads.index.max() / 4
    if not sigma2:
        sigma2 = dyads.index.max() / 5
    plt.figure()
    plt.title(sample)
    plt.xlabel('Position relative to dyad (bp)')
    plt.ylabel('Frequency' if absolute else 'Relative Frequency')
    plt.xlim(x[0], x[len(x) - 1])
    plt.xticks(list(range(x[0], x[len(x) - 1] + 1, 25)))
    plt.plot(x, y, color='red')
    plot_output = sample + (suffix if suffix else '') + '-dyad-double-gaussian.png'
    try:
        constant = ConstantModel(prefix='c_')
        pars = constant.make_params()
        pars['c_c'].set(value=dyads[yheader].min(), min=0.0, max=dyads[yheader].max())
        gauss1 = GaussianModel(prefix='g1_')
        pars.update(gauss1.make_params())
        pars['g1_center'].set(value=center1, min=cmin1, max=cmax1)
        pars['g1_sigma'].set(value=sigma1, min=smin1)
        pars['g1_amplitude'].set(value=amp1, min=amin1)
        gauss2 = GaussianModel(prefix='g2_')
        pars.update(gauss2.make_params())
        pars['g2_center'].set(value=center2, min=cmin2, max=cmax2)
        pars['g2_sigma'].set(value=sigma2, min=smin2)
        pars['g2_amplitude'].set(value=amp2, min=amin2)
        mod = constant + gauss1 + gauss2
        init = mod.eval(pars, x=x)
        out = mod.fit(y, pars, x=x)
        if components:
            plt.plot(x, init, 'b--', label='Initial fit')
        if verbose:
            print(out.fit_report(min_correl=0.5))
        plt.plot(x, out.best_fit, 'b-', label='Best fit')
        if gaussian:
            comps = out.eval_components(x=x)
            constant_y = comps['c_']
            plt.plot(x, [yv + constant_y for yv in comps['g1_']], 'm--', label='Gaussian 1')
            plt.plot(x, [yv + constant_y for yv in comps['g2_']], 'y--', label='Gaussian 2')
        if components:
            comps = out.eval_components(x=x)
            plt.plot(x, np.repeat(comps['c_'], len(x)), 'g--', label='Constant component')
            plt.plot(x, comps['g1_'], 'm--', label='Gaussian component 1')
            plt.plot(x, comps['g2_'], 'k--', label='Gaussian component 2')
    except Exception as e:
        logging.warning('could not fit double gaussian curve to sample {}'.format(sample), e)
    if components:
        plt.legend(loc='lower right')
    plt.savefig(plot_output)
    if svg:
        plot_svg_output = sample + (suffix if suffix else '') + '-dyad-double-gaussian.svg'
        plt.savefig(plot_svg_output, transparent=True)
    plt.close()


if __name__ == '__main__':
    fitdoublegaussian()
