import { getWordProportion, getDateRange } from './api.js'
import { keywordNgram, keywordSentence } from './ngram.js'
function proportionChart(data, filter) {
  const canvasWidth = (document.body.clientWidth * 10) / 13 - 100
  const canvasHeight = (canvasWidth * 3) / 4

  // 加總 Keyword 的總量
  function getSumValue(keyword, data) {
    const sum = data
      .filter((x) => x.keyword === keyword)
      .reduce((last, now) => {
        return last + now.wordCount
      }, 0)
    return sum
  }
  // 整理data的格式
  function cleanData(minDate, maxDate) {
    // 日期的filter
    let filterData = data.filter((d) => new Date(d.date) >= minDate && new Date(d.date) <= maxDate)

    let result = []
    // 計算詞頻
    filterData.reduce((res, value) => {
      if (!res[value.word + value.keyword]) {
        res[value.word + value.keyword] = { keyword: value.keyword, word: value.word, wordCount: 0 }
        result.push(res[value.word + value.keyword])
      }
      res[value.word + value.keyword].wordCount += value.wordCount
      return res
    }, {})
    // 去算比例
    result = result.map((x) => {
      x.proportion = x.wordCount / getSumValue(x.keyword, filterData)
      return x
    })
    // group起來
    let groupResult = d3.group(result, (x) => x.word)
    let newDataList = []
    // 去找那個字有沒有，沒有的話給0.0000001
    groupResult.forEach((value, keyword) => {
      let x = { proportion: 0.0000000001 }
      let y = { proportion: 0.0000000001 }
      x = value.find((d) => d.keyword === filter.keywordA) || { proportion: 0.0000000001 }
      y = value.find((d) => d.keyword === filter.keywordB) || { proportion: 0.0000000001 }
      // 過濾大於0.001的進去result
      if (!(x.proportion < 0.001 && y.proportion < 0.001)) {
        newDataList.push({
          word: keyword,
          x: x.proportion,
          y: y.proportion,
        })
      }
    })
    return [result, newDataList]
  }

  const minDate = new Date(Math.min(...data.map((p) => new Date(p.date))))
  const maxDate = new Date(Math.max(...data.map((p) => new Date(p.date))))

  const [rawResult, newDataList] = cleanData(minDate, maxDate)

  let allData = newDataList
  let startTime = 0
  let EndTime = 0
  // set the dimensions and margins of the graph
  const margin = { top: 10, right: 30, bottom: 30, left: 60 }
  // 新增svg
  const svg = d3
    .select('#proportionChart')
    .append('svg')
    .attr('width', canvasWidth + margin.right + margin.left)
    .attr('height', canvasHeight + margin.top + margin.bottom + 50)
    .attr('class', 'mx-auto')
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // X軸
  const x = d3
    .scaleLog()
    .clamp(false)
    .domain([d3.min(rawResult, (x) => x.proportion), d3.max(rawResult, (x) => x.proportion)])
    .range([0, canvasWidth])
  //
  svg
    .append('g')
    .attr('transform', `translate(0, ${canvasHeight})`)
    .call(
      d3
        .axisBottom(x)
        .ticks(2.7)
        .tickFormat(d3.format('.2%'))
        .tickSize(-canvasWidth * 1.4),
    )
    .selectAll('text')
    .style('text-anchor', 'end')
    .style('font-size', '14px')
    .attr('transform', 'rotate(-25)')

  // Y軸
  const y = d3
    .scaleLog()
    .clamp(false)
    .domain([d3.min(rawResult, (x) => x.proportion), d3.max(rawResult, (x) => x.proportion)])
    .range([canvasHeight, 0])
  svg
    .append('g')
    .call(
      d3
        .axisLeft(y)
        .ticks(2.7)
        .tickFormat(d3.format('.2%'))
        .tickSize(-canvasHeight * 1.4),
    )
    .style('font-size', '14px')

  // 給背景框框的顏色
  svg.selectAll('.tick line').attr('stroke', '#EBEBEB').attr('opacity', '0.8')
  svg.selectAll('.domain').attr('stroke', '#EBEBEB').attr('opacity', '0.8')

  // 讓圈圈不會重疊
  let simulation = d3
    .forceSimulation(allData)
    .force('collision', d3.forceCollide(11))
    .force(
      'x',
      d3.forceX((d) => {
        return x(d.x)
      }),
    )
    .force(
      'y',
      d3.forceY((d) => y(d.y)),
    )
    .on('tick', drawPlot)
  // 給上面的keyword背景顏色
  d3.select('#keywordA').style('background-color', '#FF7676')
  d3.select('#keywordB').style('background-color', '#5095FF')

  // 得到相對應的顏色
  function getColor(d) {
    const newX = x.invert(d.x)
    const newY = y.invert(d.y)
    if (newX > newY) {
      return '#FF5050'
    } else {
      return '#5095FF'
    }
  }
  // 計算透明度
  function getOpacity(d) {
    const newX = x.invert(d.x)
    const newY = y.invert(d.y)
    const maxA = Math.max(...allData.map((p) => x.invert(p.x) - y.invert(p.y)))
    const maxB = Math.max(...allData.map((p) => y.invert(p.y) - x.invert(p.x)))
    if (newX > newY) {
      return ((newX - newY) / maxA) * 0.9 + 0.1
    } else {
      return ((newY - newX) / maxB) * 0.9 + 0.1
    }
  }

  let g = svg.append('g').attr('class', 'canvas')
  simulation.stop()
  createCanvas(allData)

  function createCanvas(data) {
    // 建立circle
    g.selectAll('#proportionChart circle')
      .data(data)
      .join('circle')
      .attr('cx', (d) => {
        x(d.x)
      })
      .attr('cy', (d) => y(d.y))
      .attr('r', 10)
      .attr('fill-opacity', (d) => getOpacity(d))
      .attr('fill', (d) => getColor(d))
    // 建立文字
    g.selectAll('text')
      .data(data)
      .join('text')
      .attr('x', (d) => {
        return x(d.x)
      })
      .attr('y', (d) => {
        return y(d.y)
      })
      .style('font-size', '10px')
      .text((i) => i.word)
      .attr('class', 'word')
      .on('mouseover', (event, d) => {
        // mouseover會變大
        d3.selectAll(`text[data-propWord =${d.word}]`).transition().duration(400).style('font-size', '15px')
        d3.selectAll(`circle[data-propWord =${d.word}]`).transition().duration(400).attr('r', 20)
      })
      .on('mouseleave', (event, d) => {
        // mouseover會恢復
        d3.selectAll(`text[data-propWord =${d.word}]`).transition().duration(400).style('font-size', '10px')
        d3.selectAll(`circle[data-propWord =${d.word}]`)
          .transition()
          .duration(400)
          .attr('r', 10)
          .attr('fill-opacity', (d) => getOpacity(d))
      })
  }
  // click事件後會跳出modal
  d3.selectAll('text.word').on('click', (event, d) => {
    let date = document.querySelectorAll(`#proportionDateFilterSvg .parameter-value text`)
    let dateStart = date[0].textContent
    let dateEnd = date[1].textContent
    const element = event.target.dataset
    // body 的 滾動條隱藏
    d3.select('body').classed('overflow-y-hidden	', true)
    d3.select('#proportionModal').classed('hidden', false).classed('opacity-100', true)
    const loading = `<div role="status" class="py-44" >
                  <img src="../static/img/SK_logo.png" alt="" class="animate-bounce w-40 mx-auto" />

                  <p class="text-center text-2xl animate-pulse">Loading...</p>
                </div>`
    // 生成Modal
    function generateModal(key) {
      document.getElementById(`bigram-body-${key}`).innerHTML = ''
      document.getElementById(`trigram-body-${key}`).innerHTML = ''
      document.getElementById(`sentence-list-${key}`).innerHTML = ''
      document.getElementById(`bigram-loading-${key}`).innerHTML = loading
      document.getElementById(`trigram-loading-${key}`).innerHTML = loading
      document.getElementById(`sentence-list-${key}`).innerHTML = loading
      d3.select(`#modal-topic-${key}`).text(document.getElementById(`keyword${key}`).innerText)
      d3.select(`#modal-keyword-${key}`).text(element.propWord)
      d3.select(`#modal-dateStart-${key}`).text(dateStart)
      d3.select(`#modal-dateEnd-${key}`).text(dateEnd)
      let input = {
        type: filter.type,
        topic: document.getElementById(`keyword${key}`).innerText,
        keyword: element.propWord,
        product: filter.product,
        source: filter.source,
        dateStart: dateStart,
        dateEnd: dateEnd,
        content: filter.content,
      }
      keywordNgram(input, key)
      keywordSentence(input, key)

      const sentenceButton = document.getElementById(`sentence-button-${key}`)
    }
    generateModal('A')
    generateModal('B')
  })
  // tick的事件去drawPlot
  function drawPlot() {
    // circle生成
    d3.selectAll('#proportionChart circle')
      .data(allData)
      .attr('cx', (d) => {
        return d.x
      })
      .attr('cy', (d) => d.y)
      .attr('fill-opacity', (d) => getOpacity(d))
      .attr('fill', (d) => getColor(d))
      .attr('class', 'cursor-pointer')
      .attr('data-propWord', (d) => d.word)

    // 文字生成
    d3.selectAll('.word')
      .data(allData)
      .attr('x', (d) => d.x)
      .attr('y', (d) => d.y)
      .attr('alignment-baseline', 'middle') // Vertically align text with point
      .attr('text-anchor', 'middle')
      .text((i) => i.word)
      .attr('data-propWord', (d) => d.word)
      .attr('class', 'word cursor-pointer')

    // svg.selectAll(".word").
  }

  simulation.alpha(1)
  simulation.restart()
  d3.select('#proportionDateFilterSvg').remove()
  // 日期的filter
  const sliderRange = d3
    .sliderBottom()
    .min(minDate)
    .max(maxDate)
    .width(800)
    .fill('#D4011D')
    .tickFormat(d3.timeFormat('%Y/%m/%d'))
    .default([minDate, maxDate])
    .on('onchange', function (val) {
      // 有拉滑桿的話做更新
      simulation.stop()

      startTime = val[0]
      EndTime = val[1]

      let [_, temp] = cleanData(startTime, EndTime)
      allData = temp
      // drawPlot()
      simulation = d3
        .forceSimulation(allData)
        .force('collision', d3.forceCollide(11))
        .force(
          'x',
          d3.forceX((d) => {
            return x(d.x)
          }),
        )
        .force(
          'y',
          d3.forceY((d) => y(d.y)),
        )
        .on('tick', drawPlot)
    })

  d3.select('#proportionDateFilter').append('svg').attr('id', 'proportionDateFilterSvg').attr('preserveAspectRatio', 'xMinYMin meet').attr('viewBox', '0 0 950 600').classed('svg-content', true).append('g').attr('transform', 'translate(80,30)').call(sliderRange)
  d3.selectAll('#proportionDateFilterSvg  text').attr('font-size', '0.7em')
}

export default proportionChart
