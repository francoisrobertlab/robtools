import logging

import click
from lmfit.models import GaussianModel, ConstantModel

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd
from robtools.txt import Parser


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--components', '-c', is_flag=True,
              help='Shows fit components and initial fit in plot.')
@click.option('--gaussian', '-g', is_flag=True,
              help='Shows gaussian components scaled with the constant component.')
@click.option('--svg', is_flag=True,
              help='Save vectorial plot.')
@click.option('--verbose', '-v', is_flag=True,
              help='Shows fit report.')
@click.option('--curves', is_flag=True,
              help='Saves curve details in text file.')
@click.option('--count', type=int, default=1, show_default=True,
              help='Number of Gaussian curves to fit')
@click.option('--amin', '-am', type=float, default=None,
              help='Minimum amplitude of gaussians. Defaults to unbounded')
@click.option('--amax', '-aM', type=float, default=None,
              help='Maximum amplitude of gaussians. Defaults to unbounded')
@click.option('--smin', '-sm', type=float, default=None,
              help='Minimum width (sigma) of gaussians. Defaults unbounded')
@click.option('--smax', '-sM', type=float, default=None,
              help='Maximum width (sigma) of gaussians. Defaults unbounded')
@click.option('--suffix', default=None,
              help='Suffix to append to sample name.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def fitgaussians(samples, components, gaussian, svg, verbose, curves, count, amin, amax, smin, smax, suffix, index):
    """Fits multiple gaussian curves to dyad coverage."""
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fit_gaussians(samples, components, gaussian, svg, verbose, curves, count, amin, amax, smin, smax, suffix, index)


def fit_gaussians(samples='samples.txt', components=False, gaussian=False, svg=False, verbose=False, curves=False, count=1, amin=None, amax=None, smin=None, smax=None, suffix=None, index=None):
    """Fits multiple gaussian curves to dyad coverage."""
    sample_names = Parser.first(samples)
    if index is not None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        fit_gaussians_sample(sample, components, gaussian, svg, verbose, curves, count, amin, amax, smin, smax, suffix)


def fit_gaussians_sample(sample, components=False, gaussian=False, svg=False, verbose=False, curves=False, count=1, amin=None, amax=None, smin=None, smax=None, suffix=None):
    """Fits multiple gaussian curves to dyad coverage for a single sample."""
    print('Fits {} gaussian curves to dyad coverage of sample {}'.format(count, sample))
    input = sample + (suffix if suffix else '') + '.txt'
    data = pd.read_csv(input, sep='\t', index_col=0, comment='#')
    x = data.index.values
    yheader = data.columns[0]
    y = data[yheader].values
    amp = data[yheader].max() * 100 / count
    sigma = (data.index.max() - data.index.min()) / 2 / count
    plt.figure()
    plt.title(sample)
    plt.xlabel('Position relative to dyad (bp)')
    plt.ylabel('Frequency')
    plt.xlim(x[0], x[len(x) - 1])
    plt.xticks(list(range(x[0], x[len(x) - 1] + 1, 25)))
    plt.plot(x, y, color='red')
    plot_output = sample + (suffix if suffix else '') + '-' + str(count) + 'gaussians.png'
    try:
        constant = ConstantModel(prefix='c_')
        pars = constant.make_params()
        pars['c_c'].set(value=data[yheader].min(), min=0.0)
        mod = constant
        center_linespace = np.linspace(0, 1.0, count+2)
        for i in range(0, count):
            prefix = 'g' + str(i) + '_'
            center = (data.index.max() - data.index.min()) * center_linespace[i+1] + data.index.min()
            gauss = GaussianModel(prefix=prefix)
            pars.update(gauss.make_params())
            pars[prefix + 'center'].set(value=center)
            pars[prefix + 'sigma'].set(value=sigma, min=smin, max=smax)
            pars[prefix + 'amplitude'].set(value=amp, min=amin, max=amax)
            mod = mod + gauss
        init = mod.eval(pars, x=x)
        out = mod.fit(y, pars, x=x)
        if curves:
            curves_output = sample + (suffix if suffix else '') + '-' + str(count) + 'gaussians-curves.txt'
            curvesxy_output = sample + (suffix if suffix else '') + '-' + str(count) + 'gaussians-curvesxy.txt'
            with open(curves_output, 'w') as co, open(curvesxy_output, 'w') as cxyo:
                co.write('\t'.join(['Gaussian index', 'Amplitude', 'Center', 'Sigma', 'Height', 'Width at half maximum',
                                    'Area']))
                co.write('\n')
                for i in range(0, count):
                    prefix = 'g' + str(i) + '_'
                    columns = [i+1, out.params[prefix + 'amplitude'].value, out.params[prefix + 'center'].value,
                               out.params[prefix + 'sigma'].value, out.params[prefix + 'height'].value,
                               out.params[prefix + 'fwhm'].value,
                               1.064467 * out.params[prefix + 'height'].value * out.params[prefix + 'fwhm'].value]
                    co.write('\t'.join([str(e) for e in columns]))
                    co.write('\n')
                comps = out.eval_components(x=x)
                constant_y = comps['c_']
                columns = ['X']
                for i in range(0, count):
                    columns.append('Gaussian ' + str(i+1))
                cxyo.write('\t'.join(columns))
                cxyo.write('\n')
                for xi in range(0, len(x)):
                    columns = [xi]
                    for i in range(0, count):
                        prefix = 'g' + str(i) + '_'
                        columns.append(constant_y + comps[prefix][xi])
                    cxyo.write('\t'.join([str(e) for e in columns]))
                    cxyo.write('\n')
        if components:
            plt.plot(x, init, 'b--', label='Initial fit')
        if verbose:
            print(out.fit_report(min_correl=0.5))
        plt.plot(x, out.best_fit, 'b-', label='Best fit')
        if gaussian:
            comps = out.eval_components(x=x)
            constant_y = comps['c_']
            colors = cm.get_cmap('hsv', count+1)(np.linspace(0, 1.0, count+1))
            for i in range(0, count):
                prefix = 'g' + str(i) + '_'
                plt.plot(x, [yv + constant_y for yv in comps[prefix]], color=colors[i], linestyle='dashed',
                         label='Gaussian ' + str(i))
        if components:
            comps = out.eval_components(x=x)
            plt.plot(x, np.repeat(comps['c_'], len(x)), 'k--', label='Constant component')
            colors = cm.get_cmap('hsv', count+1)(np.linspace(0, 1.0, count+1))
            for i in range(0, count):
                prefix = 'g' + str(i) + '_'
                plt.plot(x, comps[prefix], color=colors[i], linestyle='dashed', label='Gaussian component ' + str(i))
    except Exception as e:
        logging.warning('could not fit gaussian curves to sample {}'.format(sample), e)
    if components:
        plt.legend(loc='lower right')
    plt.savefig(plot_output)
    if svg:
        plot_svg_output = sample + (suffix if suffix else '') + '-dyad-gaussian.svg'
        plt.savefig(plot_svg_output, transparent=True)
    plt.close()


if __name__ == '__main__':
    fitgaussians()
