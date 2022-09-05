import { getWordCount, getDateRange } from './api.js'

function lineChart(data, filter) {
  function hexToRgbA(hex, opacity = 0.5) {
    let c
    if (/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)) {
      c = hex.substring(1).split('')
      if (c.length == 3) {
        c = [c[0], c[0], c[1], c[1], c[2], c[2]]
      }
      c = '0x' + c.join('')
      return 'rgba(' + [(c >> 16) & 255, (c >> 8) & 255, c & 255].join(',') + ',' + opacity + ')'
    }
  }
  // 設定寬度、高度
  const canvasWidth = (document.body.clientWidth * 5) / 10 - 100
  const canvasHeight = (canvasWidth * 3) / 4
  let allData = data
  let startTime = 0
  let EndTime = 0
  // set the dimensions and margins of the graph
  const margin = { top: 10, right: 30, bottom: 30, left: 60 }
  // append the svg object to the body of the page
  const svg = d3
    .select('#lineChart')
    .append('svg')
    .attr('width', canvasWidth + margin.right + margin.left)
    .attr('height', canvasHeight + margin.top + margin.bottom + 50)
    .attr('class', 'mx-auto')
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)
  // Sort Date
  function sortByDateAscending(a, b) {
    return a.date - b.date
  }
  data.forEach((x) => {
    x.date = new Date(x.date)
  })
  data = data.sort(sortByDateAscending)
  const dateRange = d3.extent(data, function (d) {
    return new Date(d.date)
  })

  // 沒有時間的補0
  const dateList = d3.timeDay.range(dateRange[0], dateRange[1])
  dateList.map((x) => {
    return x.setTime(x.getTime() + 8 * 60 * 60 * 1000)
  })

  function fillZeroDate(data) {
    // let bankList = []
    // data.forEach((x) => {
    //   if (!(bankList.indexOf(x.word) + 1)) {
    //     bankList.push(x.word)
    //   }
    // })
    // let result = []
    // bankList.forEach((bank) => {
    //   const bankData = data.filter((x) => {
    //     return x.word === bank
    //   })
    //   const testDate = dateList.map((date) => {
    //     return _.find(bankData, { date: date }) || { word: bank, date: date, wordCount: 0 }
    //   })
    //   result = result.concat(testDate)
    // })
    return data
  }

  // Add X axis --> it is a date format
  const x = d3.scaleTime().range([0, canvasWidth])

  svg
    .append('g')
    .attr('transform', `translate(0, ${canvasHeight})`)
    .attr('class', 'Xaxis')
    .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%Y-%m')))
    .selectAll('text')
    .style('text-anchor', 'end')
    .attr('transform', 'rotate(-65)')

  // Add Y axis
  const y = d3.scaleLinear().range([canvasHeight, 0])
  svg.append('g').attr('class', 'Yaxis').call(d3.axisLeft(y))

  // color palette
  const color = d3.scaleOrdinal(d3.schemeCategory10)
  // Draw the line
  update(startTime, EndTime, data)

  // 新增銀行加入圖表
  const bankButtonForm = document.getElementById('bankButtonForm')

  bankButtonForm.addEventListener('submit', () => {
    const inputData = document.getElementById('bankButtonInput').value
    let input = filter
    input.bank = inputData
    getWordCount(input).then((res) => {
      let newData = res.data
      newData.forEach((x) => {
        x.date = new Date(x.date)
      })

      newData = newData.sort(sortByDateAscending)

      allData = allData.concat(newData)
      update(startTime, EndTime, allData)
      // const newDateMap = d3.group(newData, (d) => d.word)
    })
    d3.selectAll('button[data-type="bankDelete"]').on('click', function (x) {
      const deleteValue = x.target.dataset.value
      allData = allData.filter((x) => x.word !== deleteValue)
      update(startTime, EndTime, allData)
    })
  })

  d3.selectAll('button[data-type="bankDelete"]').on('click', function (x) {
    const deleteValue = x.target.dataset.value
    allData = allData.filter((x) => x.word !== deleteValue)
    update(startTime, EndTime, allData)
  })

  // 更新圖表
  function update(startTime, EndTime, inputData) {
    let filterData
    if (startTime == 0) {
      filterData = inputData
    } else {
      filterData = allData.filter((x) => {
        return x.date > startTime && x.date < EndTime
      })
    }
    // 修改x axis
    x.domain(
      d3.extent(filterData, function (d) {
        return new Date(d.date)
      }),
    )

    svg
      .selectAll('.Xaxis')
      .transition()
      .duration(500)
      .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%Y-%m')))
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('transform', 'rotate(-25)')

    // 修改Y axis
    y.domain([
      0,
      d3.max(filterData, function (d) {
        return d.wordCount
      }),
    ])
    svg.selectAll('.Yaxis').transition().duration(500).call(d3.axisLeft(y))

    // 補0
    filterData = fillZeroDate(filterData)
    let bank = []
    document.querySelectorAll('.bankButton').forEach((x) => {
      bank.push(x.dataset.value)
    })
    let groupData = d3.group(filterData, (x) => x.word)
    let groupSortData = new Map()
    bank.forEach((x) => {
      groupData.get(x)
      groupSortData.set(x, groupData.get(x))
    })
    // Updata the line
    svg
      .selectAll('.line')
      .data(groupSortData)
      .join('path')
      .attr('class', 'line')
      .transition()
      .duration(500)
      .attr('fill', 'none')
      .attr('stroke', function (d) {
        return hexToRgbA(color(d[0]), 0.5)
      })
      .attr('stroke-width', 5)
      .attr('d', function (d) {
        return d3
          .line()
          .x(function (d) {
            return x(d.date)
          })
          .y(function (d) {
            return y(d.wordCount)
          })(d[1])
      })
      .attr('data-value', (d) => {
        return d[0]
      })
    svg
      // First we need to enter in a group
      .selectAll('.dot')
      .data(groupSortData)
      .join('g')
      .attr('class', 'dot')
      .style('fill', (d) => color(d[0]))
      // Second we need to enter in the 'values' part of this group
      .selectAll('.point')
      .data((d) => d[1])
      .join('circle')
      .attr('class', 'point')
      .transition()
      .duration(500)
      .attr('cx', (d) => x(d.date))
      .attr('cy', (d) => y(d.wordCount))
      .attr('r', 5)
      .attr('stroke', 'white')

    d3.selectAll('.bankButton')
      .data(groupSortData)
      .transition()
      .duration(1000)
      .style('background-color', (d) => hexToRgbA(color(d[0]), 0.5))

    d3.selectAll('.bankButton')
      .on('mouseover', function (event, d) {
        const value = this.dataset.value
        d3.selectAll(`div[data-value = ${value}]`)
          .transition()
          .duration(200)
          .style('background-color', (d) => hexToRgbA(color(d[0]), 0.7))

        d3.selectAll('path.line')
          .data(groupSortData)
          .transition()
          .duration(200)
          .attr('stroke', (x) => hexToRgbA(color(x[0]), 0.2))

        d3.selectAll(`path[data-value = ${value}]`)
          .transition()
          .duration(200)
          .attr('stroke', hexToRgbA(color(d[0]), 0.9))
      })
      .on('mouseleave', function (event, d) {
        const value = this.dataset.value
        d3.selectAll(`div[data-value = ${value}]`)
          .transition()
          .duration(200)
          .style('background-color', (d) => hexToRgbA(color(d[0]), 0.5))

        d3.selectAll('path.line')
          .data(groupSortData)
          .transition()
          .duration(200)
          .attr('stroke', (x) => hexToRgbA(color(x[0]), 0.5))
      })
    d3.selectAll('path.line')
      .on('mouseover', function (event, d) {
        const value = this.dataset.value
        d3.selectAll(`div[data-value = ${value}]`)
          .transition()
          .duration(200)
          .style('background-color', (d) => hexToRgbA(color(d[0]), 0.7))

        d3.selectAll('path.line')
          .data(groupSortData)
          .transition()
          .duration(200)
          .attr('stroke', (x) => hexToRgbA(color(x[0]), 0.2))

        d3.selectAll(`path[data-value = ${value}]`)
          .transition()
          .duration(200)
          .attr('stroke', hexToRgbA(color(d[0]), 0.9))
      })
      .on('mouseleave', function (event, d) {
        const value = this.dataset.value
        d3.selectAll(`div[data-value = ${value}]`)
          .transition()
          .duration(200)
          .style('background-color', (d) => hexToRgbA(color(d[0]), 0.5))

        d3.selectAll('path.line')
          .data(groupSortData)
          .transition()
          .duration(200)
          .attr('stroke', (x) => hexToRgbA(color(x[0]), 0.5))
      })
  }
  // Date Filter
  if (document.getElementById('dateRangeFilterSvg')) {
    document.getElementById('dateRangeFilterSvg').remove()
  }

  let type = document.querySelector('input[name=type]:checked').value
  getDateRange(type)
    .then((res) => {
      return res.data
    })
    .then((data) => {
      const minDate = new Date(data.minDate)
      const maxDate = new Date(data.maxDate)
      const sliderRange = d3
        .sliderBottom()
        .min(minDate)
        .max(maxDate)
        .width(800)
        .fill('#D4011D')
        .tickFormat(d3.timeFormat('%Y/%m'))
        .default([minDate, maxDate])
        .on('onchange', function (val) {
          startTime = val[0]
          EndTime = val[1]
          update(startTime, EndTime, allData)
        })
      d3.select('#lineDateFilter').append('svg').attr('id', 'dateRangeFilterSvg').attr('preserveAspectRatio', 'xMinYMin meet').attr('viewBox', '0 0 950 600').classed('svg-content', true).append('g').attr('transform', 'translate(80,30)').call(sliderRange)
      d3.selectAll('#dateRangeFilterSvg  text').attr('font-size', '0.7em')
    })
}

export default lineChart
