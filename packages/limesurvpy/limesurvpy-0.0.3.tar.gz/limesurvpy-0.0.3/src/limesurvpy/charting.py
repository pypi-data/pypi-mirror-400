import altair as alt
import pandas as pd
from typing import List
from matplotlib.colors import LinearSegmentedColormap, to_hex, Normalize
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum
import deep_translator as dptr

from .question import Question

class ChartType(Enum):
    BAR = 'multiple_choice'
    STACKED_MATRIX = 'matrix'
    RANKS = 'ranked_items'
    HISTOGRAM = 'histogram'
    PIE = 'piechart'
    BOXPLOT = 'boxplot'

 
class Charting:

    # try to set default renderer
    renderer: str = 'html'
        
    """Default Altair display frontend, respectively, rendering API to use for displaying plots."""

    translator = dptr.GoogleTranslator(source='auto', target='en')
    """Translation for chart labels."""

    @classmethod
    def set_display_frontend(cls, renderer: str):
        """Set the Altair renderer to use for displaying charts.

        :param renderer: Renderer to use, see https://altair-viz.github.io/user_guide/display_frontends.html
        :type renderer: str
        """
        alt.renderers.enable(renderer)

    @staticmethod
    def plot_chart(type: ChartType, question: Question, items, title: str, lang: str = "en", plot_labels: bool = None, **kwargs):
                        
        if type == ChartType.BAR:
            Charting.plot_bars(items, title=title, lang=lang, plot_labels=plot_labels, **kwargs)
        elif type == ChartType.STACKED_MATRIX:
            Charting.plot_stacked_matrix(items, title=title, lang=lang, plot_labels=plot_labels, **kwargs)
        elif type == ChartType.RANKS:
            Charting.plot_rank(items, title=title, lang=lang, plot_labels=plot_labels, **kwargs)
        elif type == ChartType.HISTOGRAM:
            Charting.plot_histogram(items, title=title, lang=lang, **kwargs)
        elif type == ChartType.PIE:
            Charting.plot_pie(items, title=title, lang=lang, plot_labels=plot_labels, **kwargs)
        elif type == ChartType.BOXPLOT:
            Charting.plot_boxplot(items, title=title, lang=lang, **kwargs)
        else:
            print(f"Chart type {type} not recognized.")

    @staticmethod
    def plot_boxplot(items: pd.DataFrame, title: str, lang: str, **kwargs):

        rank_label = 'Ranked items count'
        Charting.translator.target = lang
        if lang != 'en':
            rank_label = Charting.translator.translate(rank_label)

        box = alt.Chart(data=items).encode(
            alt.X('count:Q', title=rank_label),
        ).mark_boxplot(
            color='#222222'
        )

        items['mean_val'] = items['count'].mean()
        
        mean_val = alt.Chart(data=items).encode(
            x='mean_val:Q'
        ).mark_circle(
            color='white'
        )

        (box + mean_val).properties(
            title = alt.Title(
                title, 
                anchor="start", 
                orient="bottom", 
                offset=10)
        ).show()

    @staticmethod
    def plot_histogram(items: pd.DataFrame, title: str, lang: str = "en", maxbins: int = 10, **kwargs):

        # per-chart translation
        Charting.translator.target = lang
        x_axis_title = 'Response' if lang == 'en' else Charting.translator.translate('Response')
        y_axis_title = 'Total count' if lang == 'en' else Charting.translator.translate('Total count')
        
        hist = alt.Chart(items).mark_bar().encode(
            alt.X('value', bin=alt.Bin(maxbins=maxbins), title=x_axis_title),
            alt.Y('count()', title=y_axis_title)
        ).properties(
            title=alt.Title(title,
                anchor="start",
                orient="bottom",
                offset=10)
        ).show()

    @staticmethod
    def plot_rank(items: pd.DataFrame, title: str, lang: str = "en", plot_labels: bool = True, domain_max: int = None, scale_min: int = 10, scale_max: int = 100, sort_field: str = "rank_median", sort_order: str = "ascending", **kwargs):


        # dataframe fields used for charting
        category_fieldname = 'category_labeled' if plot_labels else 'category'
        current_domain_max = items['count'].max() + 1 if domain_max is None else domain_max

        # per-chart translation
        Charting.translator.target = lang
        rank_axis_title = 'Rank' if lang == 'en' else Charting.translator.translate('Rank')
        chart_subtitle = 'Distribution of ranks. Lower rank indicates higher importance.' if lang == 'en' else Charting.translator.translate('Distribution of ranks. Lower rank indicates higher importance.')
        total_count_label = 'Total count' if lang == 'en' else Charting.translator.translate('Total count')


        # plot mean rank and include range of rank
        current_domain_max = items['rank_max'].max() + 1 if domain_max is None else domain_max

        base = alt.Chart(data=items).encode(
            alt.X('rank_mean', title=rank_axis_title, scale=alt.Scale(domain=(0.5, current_domain_max))),
            alt.Y(f'{category_fieldname}:N', title=None, sort=alt.EncodingSortField(field=sort_field, order=sort_order)),
            # size=alt.Size('count', scale=alt.Scale(range=[scale_min, scale_max]), title=total_count_label ),
            # color=alt.Color('count', title=total_count_label).scale(scheme="viridis")  
        ).mark_square(
            color='black'
        )

       
        
        med = alt.Chart(data=items).encode(
            alt.X('rank_median', title=rank_axis_title, scale=alt.Scale(domain=(0.5, current_domain_max))),
            alt.Y(f'{category_fieldname}:N', title=None, sort=alt.EncodingSortField(field=sort_field, order=sort_order)),
        ).mark_tick(
            color='black'
        )
        med = alt.layer(med.mark_square(
            color='red'
        ))

      

        range = alt.Chart(data=items).encode(
            alt.X('rank_min', scale=alt.Scale(domain=(0.5, current_domain_max))),
            alt.X2('rank_max'),
            alt.Y(f'{category_fieldname}:N', sort=alt.EncodingSortField(field=sort_field, order=sort_order)),
        ).mark_rule(
            color='darkgreen',
        )

      
        iqr = alt.Chart(data=items).encode(
            alt.X('rank_percentile_25', scale=alt.Scale(domain=(0.5, current_domain_max))),
            alt.X2('rank_percentile_75'),
            alt.Y(f'{category_fieldname}:N', sort=alt.EncodingSortField(field=sort_field, order=sort_order)),
            color=alt.Color('count', title=total_count_label).scale(scheme="lightgreyred")  
        ).mark_rect(
            stroke='black',
            size=6
        )

        top10_rank = alt.Chart(data=items).encode(
            alt.X('rank_percentile_10', scale=alt.Scale(domain=(0.5, current_domain_max))),
            alt.Y(f'{category_fieldname}:N', sort=alt.EncodingSortField(field=sort_field, order=sort_order)),            
        ).mark_tick(
            color='red'
        )

        (range + iqr + top10_rank + base + med).properties(
            title=alt.Title(title, 
                subtitle=chart_subtitle, 
                anchor="start", 
                orient="bottom", 
                offset=10)
        ).configure_axisY(
            grid=True,
            labelLimit=0,
            titlePadding=30
        ).configure_axisX(
            grid=False,
            titlePadding=20    
        ).show()

    

    @staticmethod 
    def plot_stacked_matrix(items: pd.DataFrame, title: str, response_categories: List[str], lang: str = "en", descending_scale: bool = True, plot_labels: bool = True, domain_max: int = None, **kwargs):
        
        # color scale construction        
        category_fieldname = 'category_labeled' if plot_labels else 'category'
        response_fieldname = 'response_labeled' if plot_labels else 'response'
        domain_values = list(response_categories.values()) if plot_labels else list(response_categories.keys())

        contains_nan = True if np.nan in response_categories.keys() else False
        color_count = len(response_categories) if not contains_nan else len(response_categories) - 1
                
        colormap = plt.cm.get_cmap('RdYlGn', color_count)
        if descending_scale:
            colormap = colormap.reversed()
        norm = Normalize(vmin=0, vmax=color_count)
        

        colors = [to_hex(colormap(norm(v))) for v in range(0, color_count)]
        if contains_nan:
            colors.append('#D3D3D3')  # light gray for NaN
        
        if domain_max is None:
            domain_max = items['count'].max() + 1

        # make a dictionary to specify drawing order in dataframe
        order_dict = {key: idx for idx, key in enumerate(domain_values)}
        items_copy = items.copy()
        items_copy['category_draw_order'] = items_copy[response_fieldname].map(order_dict)

        # per-chart translation
        Charting.translator.target = lang
        chart_subtitle = "Number of times an item has been ranked, irrespective of rank" if lang == 'en' else Charting.translator.translate("Number of times an item has been ranked, irrespective of rank")
        share_axis_title = 'Share of total (%)' if lang == 'en' else Charting.translator.translate('Share of total (%)')
        share_subtitle = 'Share of responses per item' if lang == 'en' else Charting.translator.translate('Share of responses per item')

        ch = alt.Chart(data=items_copy,
            title=alt.Title(title,
                subtitle=share_subtitle,
                anchor='start',
                orient='bottom', 
                offset=20
            )
        ).encode(
            alt.X('count:Q', title=share_axis_title, axis=alt.Axis(tickMinStep=1)).stack('normalize'),
            alt.Y(f'{category_fieldname}:N', title=None, sort=alt.EncodingSortField(field=category_fieldname, order='ascending')),
            color=alt.Color(f'{response_fieldname}:N', 
                            scale=alt.Scale(domain=list(domain_values), range=colors),
                            title=''),
            order=alt.Order('category_draw_order:O', sort='ascending')
        ).mark_bar().configure_axisY(
            labelLimit=0,
        ).configure_axisX(
            titlePadding=20
        ).show()


    @staticmethod
    def plot_bars(items: pd.DataFrame, title: str, lang: str = "en", plot_labels: bool = True, domain_max: int = None, **kwargs):

        # determine category field to use
        category_fieldname = 'category_labeled' if plot_labels else 'category'

        if domain_max is None:
            domain_max = items['count'].max() + 1

        # per-chart translation
        Charting.translator.target = lang
        count_axis_title = 'Total count' if lang == 'en' else Charting.translator.translate('Total count')
        chart_subtitle = "Number of times an item has been selected" if lang == 'en' else Charting.translator.translate("Number of times an item has been selected")

        base = alt.Chart(items,
            title=alt.Title(title,
                subtitle=chart_subtitle,
                anchor="start",
                orient="bottom",
                offset=20)
        ).encode(   
            y=alt.Y(f'{category_fieldname}:N', sort='-x', title=None),
            x=alt.X('count:Q').title(count_axis_title).scale(domain=(0, domain_max)),
            text=alt.Text('count')
        )
        base = alt.layer(base.mark_bar(color='darkgreen'), base.mark_text(dx=20)).configure_axisY(
            titlePadding=30
        ).configure_axisY(
            labelLimit=0
        ).show()

    
    @staticmethod
    def plot_pie(items: pd.DataFrame, title: str, lang: str = "en", plot_labels: bool = True, **kwargs):
        
        # determine category field to use
        category_fieldname = 'category_labeled' if plot_labels else 'category'

        inner_radius = kwargs.get('inner_radius', 0)

        # per-chart translation
        Charting.translator.target = lang
        chart_subtitle = "Number of times an item has been selected" if lang == 'en' else Charting.translator.translate("Number of times an item has been selected")

        # Create base chart with shared properties
        base = alt.Chart(items, 
            title=alt.Title(
                title, 
                subtitle=chart_subtitle,
                anchor="middle", 
                orient="bottom",
                offset=20)
        ).encode(
            theta=alt.Theta('count', type="quantitative", stack=True),
            color=alt.Color(category_fieldname, type="nominal", title=None),            
        )
        
        # Create the pie chart arc
        arc = base.mark_arc(
            innerRadius=inner_radius,
            outerRadius=(inner_radius + 100)
        )
        
        # Create the text labels
        text = base.mark_text(
            radius=inner_radius + 115,
            fill="black"
        ).encode(
            text=alt.Text('count:Q')
        )
        
        # Layer the arc and text together
        (arc + text).resolve_scale( 
            theta="independent" 
        ).configure_legend(
            labelLimit=0
        ).show()
