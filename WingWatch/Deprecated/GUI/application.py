# app.py
from flask import Flask, render_template, request, redirect, url_for
import plotly.graph_objects as go
import plotly
import pandas as pd
import json
import os
import numpy as np
from scipy.spatial import ConvexHull

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        # If the user does not select a file, the browser may submit an empty part
        if file.filename == '':
            return redirect(request.url)
        
        # Save the file to the upload folder
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            


            points = []
            # Compute the convex hull
            theta = np.linspace(-np.pi,np.pi,30)
            phi = np.linspace(-2*np.pi,2*np.pi,30)

            for i in phi:
                for j in theta:       
                    points.append(points_for_sphere(i,j))

            points = np.row_stack(points)

            tess_sphere = ss.ConvexHull(points)


            hull = tess_sphere

            fig = go.Figure()

            # Add the points

            fig.add_trace(go.Scatter3d(
                x=points[0, :], y=points[1, :], z=points[2, :],
                mode='markers',
                marker=dict(size=5, color='blue'),
                name='Points'
            ))

            # Add the convex hull
            for simplex in hull.simplices:
                fig.add_trace(go.Mesh3d(
                    x=points.T[simplex, 0],
                    y=points.T[simplex, 1],
                    z=points.T[simplex, 2],
                    color='red',
                    opacity=0.5,
                    name='Convex Hull'
                ))


            # Set the title and labels
            fig.update_layout(
                title='3D Convex Hull',
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z'
                )
            )

            # Show plot
            fig.show()

            # Read the CSV file into a DataFrame
            df = pd.read_csv(filepath)
            
            """
            # Generate a Plotly figure from the DataFrame
            fig = go.Figure(data=[
                go.Scatter(
                    x=df[df.columns[0]],  # Use the first column as X-axis
                    y=df[df.columns[1]],  # Use the second column as Y-axis
                    mode='lines+markers'
                )
            ])
            """

            # Convert the figure to JSON for rendering in the template
            graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
            return render_template('index.html', graph_json=graph_json)
    
    # For GET requests, just render the upload form
    return render_template('index.html')

def points_for_sphere(theta,phi,offset_x = 0,offset_y=0,offset_z=0):
    x = np.sin(theta) * np.cos(phi) + offset_x
    y = np.sin(theta) * np.sin(phi) + offset_y
    z = np.cos(theta)  +offset_z
    return np.array([x,y,z])


if __name__ == '__main__':
    app.run(debug=True)
