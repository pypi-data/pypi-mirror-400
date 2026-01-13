# amp-depth-viz
## visualise amplicon genome coverage by bokeh using mosdepth output

## install
```
    git clone https://github.com/abcdtree/amp-depth-viz.git
    cd amp-depth-viz
    conda create -y conda.yaml
    pip install dist/amp_depth_viz-0.0.1.tar.gz
```

## Usage
```
    amp-depth-viz src/amp_depth_viz/sample/sample_input.bed --ylim 300 --threshold 40 --output test.html
```
