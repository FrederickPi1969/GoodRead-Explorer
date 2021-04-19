import * as d3 from 'd3';
import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import { renderErrorReport } from './error';
import {HOST, ROUTE_BOOK, ROUTE_AUTHOR, ROUTE_SEARCH, ROUTE_AUTHORS} from './main.js';
import Slider from '@material-ui/core/Slider';

let drawChart = function(data) {
    /**
     * Draw the bar chart in the #chart element.
     * Reference - https://bl.ocks.org/d3noob/8952219.
     */
    let margin = {top: 30, right: 30, bottom: 70, left: 80};
    let minWidth = 480;
    let pendingWidth = 42 * data.length;
    let width = (pendingWidth < minWidth ? minWidth : pendingWidth) - margin.left - margin.right;
    let height = 360 - margin.top - margin.bottom;

    d3.select('svg').remove(); // prevent multiple charts shown
    let svg = d3.select('#chart')
    .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
    .append('g')
        .attr('transform',
            'translate(' + margin.left + ',' + margin.top + ')');

    // X axis
    let x = d3.scaleBand()
    .range([ 0, width ])
    .domain(data.map(function(d) { return d._id; }))
    .padding(0.2);
    svg.append('g')
    .attr('transform', 'translate(0,' + height + ')')
    .call(d3.axisBottom(x))
    .selectAll('text')
        .attr('id', 'x_tick')
        .attr('transform', 'translate(-10,0)rotate(-45)')
        .style('text-anchor', 'end')
        .style('cursor', 'pointer');
        
    
    let id2index = {};
    for (let i = 0; i < data.length; i++) { id2index[data[i]._id] = i; }

    let urlAttr = 'book_url' in data[0] ? 'book_url' : 'author_url';
    d3.selectAll('.tick')
    .on('click', function (even, id) {
        let index = id2index[id];
        let url = data[index][urlAttr];
        window.open(url, '_blank');
    });

    // Add Y axis
    let y = d3.scaleLinear()
    .domain([4.0, 5.0])
    .range([ height, 0]);
    svg.append('g')
    .call(d3.axisLeft(y));

    // Bars
    svg.selectAll('mybar')
    .data(data)
    .enter()
    .append('rect')
        .attr('x', function(d) { return x(d._id); })
        .attr('y', function(d) { return y(d.rating_value); })
        .attr('width', x.bandwidth())
        .attr('height', function(d) { return height - y(d.rating_value); })
        .attr('fill', '#d8780a')

}


let ChartDrawer = function(props) {
    /**
     * Function component for the wrapper of the SVG element.
     */
    let data = props.data;
    let topK = props.top_k;
    let dataToShow = data.slice(0, topK);
    useEffect(() => drawChart(dataToShow), [dataToShow]);
    return (
        <div id="chart">
        </div>
    );
} 


class RankRenderer extends React.Component {
    /**
     * HTML component for scenes where users want to visualize
     * the top-K rated authors/books.
     */
    constructor(props) {
        super(props);
        this.fetchData();
        this.state = {data : null, topK : 10}
        this.handleChange = this.handleChange.bind(this);
    }

    sortData(rawData) {
        /**
         * Sort database based on rating_value.
         * Store the result in this.state.
         */
        let sortedData = rawData.sort(
            // sort with descending order
            function (a, b) {return b.rating_value - a.rating_value;}
        );
        this.setState({data : sortedData});
    }

    async fetchData() {
        /**
         * Fetch the entire book/author database to local.
         */
        let queryString = this.props.db + '._id : "*"'; // get all instance with wildcard
        let params =  new URLSearchParams({q : queryString});
        let url = HOST + ROUTE_SEARCH + '?' + params;
        let rawData;
        await d3.json(url).then(data => rawData = data);
        this.sortData(rawData);
    }

    handleChange(event, newValue) {
        /**
         * When users drag the slider,
         * change topK in this.state correspondingly.
         */
        this.setState({topK : newValue});
    }

    render() {
        let dbName = this.props.db === 'book' ? 'Book' : 'Author';
        if (this.state.data === null) {
            return <h1 className={'page_center'}> Loading...</h1>
        }
        return(
            <div>
                <h1>Top {this.state.topK} Rated {dbName}s</h1>
                <ChartDrawer data={this.state.data} top_k={this.state.topK}/>
                <div id="slider_container">
                    <Slider
                        defaultValue={this.state.topK}
                        aria-labelledby="discrete-slider-always"
                        step={1}
                        valueLabelDisplay="on"
                        min={5}
                        max={20}
                        onChange={this.handleChange}
                    />
                </div>
            </div>
        );
    }
}


let renderRank = function(db) {
    /**
     * Interface for adding the RandRenderer into HTML.
     */
    ReactDOM.render(<RankRenderer db={db}/>, document.getElementById('root'))
}

export {renderRank};