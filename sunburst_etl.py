import pandas as pd
import random


def load_data():
    data = pd.read_csv("/Users/doc/Desktop/Work/Projects (2021)/Sunburst/order_superstore.csv")
    data['Year'] = pd.to_datetime(data['Order Date'].astype(str), format='%d/%m/%Y').dt.year
    data['Year'] = data['Year'].astype(str)
    return data


def agg_data(data, group_cols):
    data = data[group_cols + ['Year', 'Profit', 'Sales']] \
        .groupby(group_cols + ['Year']) \
        .sum() \
        .reset_index()
    data['Budget'] = data['Sales'] * 0.75
    data = data.pivot(index=group_cols, columns='Year', values=['Profit', 'Sales', 'Budget']).reset_index()
    data.set_axis(data.columns.map('_'.join), axis=1, inplace=True)
    data.reset_index()
    return data


def sunburst_data(data):
    cat_cols = [col for col in data.columns if not pd.api.types.is_numeric_dtype(data[col])]
    val_cols = [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])]

    sb_df = pd.DataFrame()

    agg_col_list = []

    # Loop over the list, starting with the first item and ending with the last item
    for i in range(len(cat_cols)):
        # Create a sublist starting with the first item and ending with the current item in the loop
        sublist = cat_cols[:i + 1]
        # Add the sublist to the new list
        agg_col_list.append(sublist)

    for j, col in enumerate(agg_col_list):
        agg = data.groupby(agg_col_list[j])[val_cols].sum().reset_index()
        agg['component'] = agg[col].apply(lambda x: ">".join(x), axis=1)
        agg['level'] = j + 1
        sb_df = pd.concat([sb_df, agg], axis=0)

    meta_df = pd.DataFrame(
        {
            "level": [1, 2, 3, 4],
            "distance": [1.5, 2.5, 3.5, 4.25],
            "width": [1, 1, 0.75, 0.35],
        }
    )

    path_df = pd.DataFrame({'path': range(1, 363)})
    sb_df = pd.merge(left=sb_df, right=meta_df, how='left')
    sb_df = pd.merge(left=sb_df, right=path_df, how='cross')
    sb_df['sunburst_type'] = cat_cols[0]
    sb_df = sb_df.sort_values(by=['Sub-Category_', 'Sales_2017'])
    return sb_df


if __name__ == "__main__":

    group_cols1 = ['Segment', 'Region', 'Category', 'Sub-Category']
    group_cols2 = ['Region', 'Category', 'Segment', 'Sub-Category']
    group_cols3 = ['Category', 'Segment', 'Region', 'Sub-Category']
    g_lists = [group_cols1, group_cols2, group_cols3]

    sb_output = pd.DataFrame()

    for g in g_lists:
        d = load_data()
        d = agg_data(d, g)
        s = sunburst_data(d)
        sb_output = pd.concat([sb_output, s])

    sb_output.to_csv('sb_output.csv', encoding='UTF-8')
