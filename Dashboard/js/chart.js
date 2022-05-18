/////////////////////////////////////////////////////////////////////////////
// JS chart creation using ChartJS 
// This program will create all of the dashboard charts using these sources: 
// chartweeks.json: metrics by week (overall metrics)
// charworkoutdays.json: any daily metrics, currently used for power and SPI
// chartmetrics.json: single metrics for the individual stats

// Copyright (C) 2022  Jeff Schroeder
/////////////////////////////////////////////////////////////////////////////
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see https://www.gnu.org/licenses/
////////////////////////////////////////////////////////////////////////////
// TODO
// jQuery .ready function is used to open and read the json files. Currently I cannot figure out how to make the jsondata variable global, so
// I had to keep the function open for all the processing and chart creation.

//Update chart defaults
//ChartJS is being used for the charts. This updates the global defaults so they don't have to be listed for each
Chart.defaults.global.responsive = true;
Chart.defaults.global.maintainAspectRatio = false;
Chart.defaults.global.legend.position = 'bottom';
Chart.defaults.global.legend.labels.usePointStyle = true;
Chart.defaults.global.hover.mode= 'nearest';
Chart.defaults.global.hover.intersect= true;
Chart.defaults.scale.gridLines.drawOnChartArea = false;
Chart.defaults.scale.scaleLabel.display = true;
Chart.defaults.global.elements.line.fill = false;
var defaultcolor = '#2b90d9';
var secondcolor = 'darkgray';
var thirdcolor = 'green';

//CURRENT PROGRESS chart
//As noted above, currently have to do everything within this function
$().ready(function(){
  $.getJSON( "data/chartweeks.json", function( jsondata ) {
   var labels = jsondata.map(function(e) {
   return e.Week;
   });
   //I started with two projected paths, but later changed it to linear and polynomial projections. Left this here in case it's preferred
   // var path36 = jsondata.map(function(e) {
   //    return e.Total36;
   // });
   // var path32 = jsondata.map(function(e) {
   //    return e.Total32;
   // });
   var pathAct = jsondata.map(function(e) {
      return e.TotalActual;
   });
   var TrendEx = jsondata.map(function(e) {
      return e.TrendEx;
   });
   var TrendLin = jsondata.map(function(e) {
      return e.TrendLin;
   });

//CURRENT PROGRESS Configuration
   var chart36wk = document.getElementById('36weeks').getContext('2d');
   var config36wk = {
      type: 'line',
      data: {
         labels: labels,
         datasets: [{
            label: 'Actual',
            data: pathAct,
            borderColor: defaultcolor,
            backgroundColor: defaultcolor
         },
         {
            label: 'Trend Top',
            data: TrendEx,
            borderColor: secondcolor,
            backgroundColor: secondcolor,
            borderDash: [5,5],
            pointRadius: 0
         },
         {
            label: 'Trend Bottom',
            data: TrendLin,
            borderColor: secondcolor,
            backgroundColor: secondcolor,
            borderDash: [5,5],
            pointRadius: 0
         // },
         // {
         //    label: '32-week path',
         //    data: path32,
         //    borderColor: secondcolor,
         //    backgroundColor: secondcolor,
         //    borderDash: [5,5],
         //    pointRadius: 0
         // },
         // {
         //    label: '36-week path',
         //    data: path36,
         //    borderColor: secondcolor,
         //    backgroundColor: secondcolor,
         //    borderDash: [5,5],
         //    pointRadius: 0
         }],
      },
      options: {
         legend: {
            display: false
         },
         scales: {
            xAxes: [{
              scaleLabel: {
                labelString: 'Week'
              },
              ticks: {
                autoSkip: true,
                maxRotation: 0
              }
            }],
            yAxes: [{
              scaleLabel: {
                labelString: 'Total meters (thousands)'
              }
            }]
         }
      }
   };

   var Mainchart = new Chart(chart36wk, config36wk);
   });
});

//POWER and SPI Charts
$().ready(function(){
  $.getJSON( "data/chartworkoutdays.json", function( jsondata ) {
   var labels = jsondata.map(function(e) {
   return e.Day;
   });

   var AvgPower = jsondata.map(function(e) {
      return e.AvgWatts;
   });
   //Can plot max power as well; have left that out for now
   // var MaxPower = jsondata.map(function(e) {
   //    return e.MaxWatts;
   // });
   var Trend = jsondata.map(function(e) {
      return e.Trend;
   });

   var spi = jsondata.map(function(e) {
      return e.SPI;
   });

   //Power Chart 
   var chartPower = document.getElementById('power').getContext('2d');
   var configPower = {
      type: 'line',
      data: {
         labels: labels,
         datasets: [{
            label: 'Avg Power',
            data: AvgPower,
            borderColor: 'rgb(255,255,255,0)', //lazy way to make a scatter plot instead of changing the chart type
            backgroundColor: defaultcolor,
            cubicInterpolationMode: 'monotone'
         // },
         // {
         //    label: 'Max Power',
         //    data: MaxPower,
         //    borderColor: 'rgb(255,255,255,1)',
         //    backgroundColor: 'rgb(0,0,0,0)',
         //    cubicInterpolationMode: 'monotone'
            },
            {
            label: 'Trend',
            data: Trend,
            borderColor: thirdcolor,
            backgroundColor: thirdcolor,
            pointRadius: 0
         }]
      },
      options: {
         legend: {
            display: false
         },
         scales: {
            xAxes: [{
              scaleLabel: {
                labelString: 'Rows (10+ min)'
            },
              ticks: {
                autoSkip: true,
                maxTicksLimit: 2,
                maxRotation: 0
              }
            }],
            yAxes: [{
              scaleLabel: {
                labelString: 'Power (watts)'
              }
            }]
         }
      }
   };

   //SPI Chart 
   var chartSPI = document.getElementById('spi').getContext('2d');
   var configSPI = {
      type: 'line',
      data: {
         labels: labels,
         datasets: [{
            label: 'SPI',
            data: spi,
            borderColor: 'rgb(255,255,255,0)', //lazy way to make a scatter plot instead of changing the chart type
            backgroundColor: defaultcolor,
            cubicInterpolationMode: 'monotone'
         }]
      },
      options: {
         legend: {
            display: false
         },
         scales: {
            xAxes: [{
              scaleLabel: {
                labelString: 'Rows (10+ min)'
            },
              ticks: {
                autoSkip: true,
                maxTicksLimit: 2,
                maxRotation: 0
              }
            }],
            yAxes: [{
              scaleLabel: {
                labelString: 'SPI (avg watts/spm)'
              }
            }]
         }
      }
   };

   var Powerchart = new Chart(chartPower, configPower);
   var SPIchart = new Chart(chartSPI, configSPI);
   });
});

//4 METRICS BOXES (to the right of the main chart)
$().ready(function(){
  $.getJSON("data/chartmetrics.json", function( jsondata ) {

   //Box 1: Current Week
   var week = jsondata.map(function(e) {
      return e.Week;
      });
   $('#currentWeek').html(week);
   
   //Box 2 Percent Complete
   var totalM = jsondata.map(function(e) {
      return e.CurrentTotalM;
      });
   var percom = jsondata.map(function(e) {
      return e.PercentComplete;
      });

   $('#percentComplete').css('width', percom); //Set bar width
   $('#percentComplete').html(totalM+"K"); //comment out until %complete is >16% so the number isn't cut off (lazy way)

   //Box 3: Number of days rowed
   var rowdays = jsondata.map(function(e) {
      return e.RowDays;
      });
   $('#rowDays').html(rowdays);
   
   //Box 4: Average meters per row day
   var mperday = jsondata.map(function(e) {
      return e.AvgMperDay; 
      });
   $('#avgMperday').html(mperday);
   });
});