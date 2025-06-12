import matplotlib
matplotlib.use('Agg') # THIS LINE MUST BE THE FIRST MATPLOTLIB-RELATED IMPORT

import pandas as pd
import json
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

def create_plot_from_df(df, plot_type, column=None, x_column=None, y_column=None):
    """
    Generates a plot (histogram, boxplot, countplot, scatterplot) and returns it as a base64 encoded string.
    """
    # Set a dark style for plots to match the dashboard aesthetic
    plt.style.use('dark_background') 
    plt.figure(figsize=(10, 6))
    
    try:
        if plot_type == 'histogram' and column:
            sns.histplot(df[column].dropna(), kde=True, color='skyblue')
            plt.title(f'Histogram of {column}', color='white')
            plt.xlabel(column, color='white')
            plt.ylabel('Frequency', color='white')
            plt.tick_params(axis='x', colors='white')
            plt.tick_params(axis='y', colors='white')
        elif plot_type == 'boxplot' and column:
            sns.boxplot(y=df[column].dropna(), color='lightcoral')
            plt.title(f'Box Plot of {column}', color='white')
            plt.ylabel(column, color='white')
            plt.tick_params(axis='x', colors='white')
            plt.tick_params(axis='y', colors='white')
        elif plot_type == 'countplot' and column:
            sns.countplot(y=df[column].dropna(), order=df[column].value_counts().index, color='lightgreen')
            plt.title(f'Count Plot of {column}', color='white')
            plt.xlabel('Count', color='white')
            plt.ylabel(column, color='white')
            plt.tick_params(axis='x', colors='white')
            plt.tick_params(axis='y', colors='white')
        elif plot_type == 'scatterplot' and x_column and y_column:
            sns.scatterplot(x=df[x_column], y=df[y_column], color='orange')
            plt.title(f'Scatter Plot of {x_column} vs {y_column}', color='white')
            plt.xlabel(x_column, color='white')
            plt.ylabel(y_column, color='white')
            plt.tick_params(axis='x', colors='white')
            plt.tick_params(axis='y', colors='white')
        else:
            plt.close() # Close figure if no valid plot type/columns
            return None

        # Set facecolor and edgecolor for the plot area and figure
        plt.gca().set_facecolor('#282c34') # Dark background for the plot area
        plt.gcf().set_facecolor('#282c34') # Dark background for the entire figure

        # Save plot to a BytesIO object
        buffer = BytesIO()
        plt.tight_layout() # Adjust layout to prevent labels from overlapping
        plt.savefig(buffer, format='png')
        plt.close() # Close the plot to free up memory

        # Encode to base64
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error creating plot for {plot_type}, column {column}: {e}")
        plt.close()
        return None

def perform_auto_analysis(file_content, file_extension):
    """
    Automatically performs data analysis based on the nature of the data.
    Generates tables, charts, and key statistics.
    """
    try:
        if file_extension == 'csv':
            # Try reading with utf-8 first, then 'latin1' if it fails
            try:
                df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
            except UnicodeDecodeError:
                df = pd.read_csv(io.StringIO(file_content.decode('latin1')))
        elif file_extension == 'xlsx':
            df = pd.read_excel(io.BytesIO(file_content))
        elif file_extension == 'json':
            df = pd.read_json(io.StringIO(file_content.decode('utf-8')))
        else:
            return {'error': 'Unsupported file type. Please upload CSV, XLSX, or JSON.'}

        # Drop columns that are entirely empty
        df.dropna(axis=1, how='all', inplace=True)
        if df.empty:
            return {'error': 'The uploaded file contains no usable data after removing empty columns.'}

        analysis_results = {}
        
        # 1. Basic Data Info (formatted as HTML)
        buffer = io.StringIO()
        df.info(buf=buffer)
        # Convert df.info() to a more structured HTML for better styling
        info_lines = buffer.getvalue().split('\n')
        info_html = "<table>"
        for line in info_lines:
            if line.strip() and not line.startswith('<class') and not line.startswith('---') and not line.startswith('Memory usage'):
                if 'Dtype' in line:
                    info_html += f"<tr><td colspan='2'><b>{line.strip()}</b></td></tr>"
                else:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        info_html += f"<tr><td>{parts[0]}</td><td>{' '.join(parts[1:])}</td></tr>"
        info_html += "</table>"
        analysis_results['data_info'] = f"<h3>Data Information</h3>{info_html}"


        # 2. Missing Values
        missing_data = df.isnull().sum()
        missing_data = missing_data[missing_data > 0] # Only show columns with missing values
        if not missing_data.empty:
            analysis_results['missing_values'] = f"<h3>Missing Values</h3>{missing_data.to_frame('Missing Count').to_html(classes='table table-dark table-striped table-bordered')}"
        else:
            analysis_results['missing_values'] = "<h3>Missing Values</h3><p>No missing values found.</p>"

        # Separate numerical and categorical columns
        numerical_cols = df.select_dtypes(include=['number']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        # Convert potential numerical columns stored as objects to numeric if possible
        for col in categorical_cols:
            if pd.to_numeric(df[col], errors='coerce').notna().all():
                df[col] = pd.to_numeric(df[col], errors='coerce')
                numerical_cols = numerical_cols.append(pd.Index([col]))
                categorical_cols = categorical_cols.drop(col)
        
        numerical_cols = numerical_cols.unique()
        categorical_cols = categorical_cols.unique()


        # 3. Descriptive Statistics for Numerical Data
        if not numerical_cols.empty:
            analysis_results['numerical_summary'] = f"<h3>Numerical Data Summary Statistics</h3>{df[numerical_cols].describe().to_html(classes='table table-dark table-striped table-bordered')}"
            
            analysis_results['numerical_plots'] = {}
            for col in numerical_cols:
                if df[col].nunique() > 1: 
                    hist_plot = create_plot_from_df(df, 'histogram', column=col)
                    box_plot = create_plot_from_df(df, 'boxplot', column=col)
                    if hist_plot and box_plot:
                        analysis_results['numerical_plots'][col] = {
                            'histogram': hist_plot,
                            'boxplot': box_plot
                        }
        else:
            analysis_results['numerical_summary'] = "<p>No numerical columns found for summary statistics or plots.</p>"


        # 4. Frequency Tables and Count Plots for Categorical Data
        if not categorical_cols.empty:
            analysis_results['categorical_summary'] = "<h3>Categorical Data Frequencies</h3>"
            analysis_results['categorical_plots'] = {}
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                if len(value_counts) > 50: 
                    analysis_results['categorical_summary'] += f"<h4>{col} Frequencies (Top 50)</h4>{value_counts.head(50).to_frame('Count').to_html(classes='table table-dark table-striped table-bordered')}"
                else:
                    analysis_results['categorical_summary'] += f"<h4>{col} Frequencies</h4>{value_counts.to_frame('Count').to_html(classes='table table-dark table-striped table-bordered')}"
                
                if df[col].nunique() > 1 and df[col].nunique() < 50: 
                    count_plot = create_plot_from_df(df, 'countplot', column=col)
                    if count_plot:
                        analysis_results['categorical_plots'][col] = count_plot
                elif df[col].nunique() >= 50:
                    analysis_results['categorical_plots'][col] = 'Too many unique values to plot meaningfully.'
        else:
            analysis_results['categorical_summary'] = "<p>No categorical columns found for frequency analysis or plots.</p>"

        # 5. Correlation Matrix for Numerical Data
        if len(numerical_cols) >= 2:
            correlation_matrix = df[numerical_cols].corr()
            analysis_results['correlation_matrix'] = f"<h3>Correlation Matrix</h3>{correlation_matrix.to_html(classes='table table-dark table-striped table-bordered')}"
        else:
            analysis_results['correlation_matrix'] = "<p>Insufficient numerical columns for correlation analysis (at least 2 required).</p>"

        # 6. Scatter Plots for top 5 numerical pairs (based on highest absolute correlation)
        if len(numerical_cols) >= 2:
            analysis_results['scatter_plots'] = {}
            correlations = df[numerical_cols].corr().abs().unstack()
            sorted_correlations = correlations.sort_values(ascending=False)
            
            plotted_pairs = set()
            count = 0
            for (col1, col2), value in sorted_correlations.items():
                if col1 == col2 or (col2, col1) in plotted_pairs:
                    continue
                
                if count >= 5: # Limit to top 5 pairs by absolute correlation
                    break

                scatter_plot = create_plot_from_df(df, 'scatterplot', x_column=col1, y_column=col2)
                if scatter_plot:
                    analysis_results['scatter_plots'][f"{col1}_vs_{col2}"] = scatter_plot
                    plotted_pairs.add((col1, col2))
                    count += 1
            
            if not analysis_results['scatter_plots'] and len(numerical_cols) >= 2:
                analysis_results['scatter_plots_info'] = "<p>No suitable numerical pairs found for scatter plots (or data variation too low).</p>"
        else:
            analysis_results['scatter_plots_info'] = "<p>Insufficient numerical columns for scatter plots.</p>"


        return {'results': analysis_results}

    except FileNotFoundError:
        return {'error': 'File not found.'}
    except pd.errors.EmptyDataError:
        return {'error': 'The uploaded file is empty or malformed. Please check its content.'}
    except pd.errors.ParserError as e:
        return {'error': f'Could not parse the file. Please ensure it is a valid CSV, XLSX, or JSON. Parser error: {e}'}
    except Exception as e:
        print(f"Analysis error: {e}") 
        return {'error': f'An unexpected error occurred during analysis: {str(e)}. Please check your file format and content.'}