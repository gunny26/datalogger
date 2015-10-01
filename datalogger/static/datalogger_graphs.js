function draw_virtualMachineCpuStats(canvas, hostname, instance, idle, ready, system, used, wait) {
    $(canvas).highcharts({
        chart: {
            type: 'spline'
        },
        title: {
            text: 'CPU time consumption of CPU #'+ instance + " on " + hostname
        },
        subtitle: {
            text: 'CPU time consumption'
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: { // don't display the dummy year
                month: '%e. %b',
                year: '%b'
            },
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'ms'
            },
            min: 0
        },
        tooltip: {
            headerFormat: '<b>{series.name}</b><br>',
            pointFormat: '{point.x:%e. %b}: {point.y:.2f} m'
        },

        plotOptions: {
            spline: {
                marker: {
                    enabled: false
                }
            }
        },

        series: [{
            name: 'idle',
            data: idle,
        },
        {
            name: 'ready',
            data: ready,
        },
        {
            name: 'system',
            data: system,
        },
        {
            name: 'used',
            data: used,
        },
        {
            name: 'wait',
            data: wait,
        },
        ]
    });
}

function draw_VirtualMachineDatastoreStats_latency(canvas, hostname, instance, readLatency, writeLatency) {
    $(canvas).highcharts({
        chart: {
            type: 'spline'
        },
        title: {
            text: 'Latency of ' + hostname + " on " + instance
        },
        subtitle: {
            text: 'Read and Write latency for datastore'
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: { // don't display the dummy year
                month: '%e. %b',
                year: '%b'
            },
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'ms'
            },
            min: 0
        },
        tooltip: {
            headerFormat: '<b>{series.name}</b><br>',
            pointFormat: '{point.x:%e. %b}: {point.y:.2f} m'
        },

        plotOptions: {
            spline: {
                marker: {
                    enabled: false
                }
            }
        },

        series: [{
            name: 'datastore.totalReadLatency.average',
            data: readLatency,
        },
        {
            name: 'datastore.totalWriteLatency.average',
            data: writeLatency,
        }]
    });
}

function draw_VirtualMachineDatastoreStats_iops(canvas, hostname, instance, series1, series2) {
    $(canvas).highcharts({
        chart: {
            type: 'spline'
        },
        title: {
            text: 'IO Operations of ' + hostname + " on " + instance 
        },
        subtitle: {
            text: 'Read and Write operations of datastore'
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: { // don't display the dummy year
                month: '%e. %b',
                year: '%b'
            },
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'IO Operations'
            },
            min: 0
        },
        tooltip: {
            headerFormat: '<b>{series.name}</b><br>',
            pointFormat: '{point.x:%e. %b}: {point.y:.2f} m'
        },

        plotOptions: {
            spline: {
                marker: {
                    enabled: false
                }
            }
        },

        series: [{
            name: 'datastore.numberReadAveraged.average',
            data: series1,
        },
        {
            name: 'datastore.numberWriteAveraged.average',
            data: series2,
        }]
    });
}

function draw_VirtualMachineDatastoreStats_transfer(canvas, hostname, instance, series1, series2) {
    $(canvas).highcharts({
        chart: {
            type: 'spline'
        },
        title: {
            text: 'IO Transfer Rate of ' + hostname + " on " + instance 
        },
        subtitle: {
            text: 'Read and Write transferrate of datastore'
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: { // don't display the dummy year
                month: '%e. %b',
                year: '%b'
            },
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'Transfer rate kB/s'
            },
            min: 0
        },
        tooltip: {
            headerFormat: '<b>{series.name}</b><br>',
            pointFormat: '{point.x:%e. %b}: {point.y:.2f} m'
        },

        plotOptions: {
            spline: {
                marker: {
                    enabled: false
                }
            }
        },

        series: [{
            name: 'datastore.read.average',
            data: series1,
        },
        {
            name: 'datastore.write.average',
            data: series2,
        }]
    });
}

function draw_develop(canvas, keys, value_keys, data) {
    $(canvas).highcharts({
        chart: {
            type: 'spline'
        },
        title: {
            text: 'Counter for key ' + keys + " values " + value_keys 
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: { // don't display the dummy year
                month: '%e. %b',
                year: '%b'
            },
            title: {
                text: 'Datetime'
            }
        },
        yAxis: {
            title: {
                text: 'unit according to measured counter'
            },
            min: 0
        },
        tooltip: {
            headerFormat: '<b>{series.name}</b><br>',
            pointFormat: '{point.x:%e. %b}: {point.y:.2f} '
        },

        plotOptions: {
            spline: {
                marker: {
                    enabled: false
                }
            }
        },

        series: data
    });
}