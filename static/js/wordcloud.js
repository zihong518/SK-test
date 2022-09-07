import { getWordCloud } from './api.js'
import { Ngram, sentence } from './ngram.js'
function wordCloud(filter, bankLength) {
  // 主要的element
  const main = document.getElementById('canvas')
  // 不同的svg有不同的filter.id
  const idName = filter.id

  // 如果沒有特定的日期區間的話
  if (!document.getElementById(filter.dateGroup)) {
    // 建立div並給id加進去main裡
    const group = document.createElement('div')
    group.setAttribute('id', filter.dateGroup)
    group.setAttribute('class', 'flex flex-col	')
    main.appendChild(group)
    // 增加此日期的element
    const date = document.createElement('p')
    date.setAttribute('class', 'text-xl  mx-auto px-3 py-1 bg-green-100 rounded-md')
    date.innerText = filter.dateStart + '~' + filter.dateEnd
    group.appendChild(date)
    // 增加這個日期的文字雲group
    const bankGroup = document.createElement('div')
    bankGroup.setAttribute('id', filter.bankGroup)
    bankGroup.setAttribute('class', 'flex ')
    group.appendChild(bankGroup)
  }
  //
  // 新增id為所屬bank的div
  const canvas = document.createElement('div')
  canvas.setAttribute('id', idName)
  // 選擇所屬的group並且加進去所屬bank的element
  const group = document.getElementById(filter.bankGroup)
  group.appendChild(canvas)
  // 顏色的列表
  const fill = d3.schemeCategory10
  // 將文字大小依照詞頻作為調整
  const tokenize = function (words) {
    const countList = words.map((x) => x.size)
    const max = Math.max(...countList)
    const min = Math.min(...countList)

    return words.map((x) => {
      return {
        text: x.text,
        size: selectSizeFactor(min, max, x.size),
      }
    })
  }
  // 將詞頻標準化
  const selectSizeFactor = function (min, max, value) {
    const a = (max - min) / (10 - 1)
    const b = max - a * 10
    return (value - b) / a
  }

  // 畫布的寬度
  const canvasWidth = (document.body.clientWidth * 5) / 6 - 100
  // 文字雲的寬度
  const cloudWidth = canvasWidth / bankLength
  // 文字雲的高度
  const cloudHeight = (cloudWidth * 3) / 4
  // 
  const margin = { top: 10, right: 10, bottom: 10, left: 10 }
  // 選擇特定的bank並且增加svg設定高度寬度等等等
  const svg = d3
    .select('#' + idName)
    .append('svg') 
    .attr('width', cloudWidth + 10)
    .attr('height', cloudHeight + margin.top + margin.bottom)
    .attr('id', 'wordCloudSvg')
    .attr('class', 'mx-auto')
    .append('g')
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
  // 選擇特定的bank增加標題文字
  d3.select('#' + idName)
    .append('p')
    .attr('class', 'text-center text-xl mb-5')
    .text(filter.bank)
  
    // 去request詞頻回來
  getWordCloud(filter).then((data) => {
    let myWords = []
    data.data.map((x) => {
      myWords.push({
        text: x._id,
        size: x.wordCount,
      })
    })
    // 將詞頻轉為文字的size
    myWords = tokenize(myWords)
    // 依照size排序文字
    myWords = myWords.sort((a, b) => b.size - a.size)
    // 只截前50
    myWords = myWords.slice(0, 50)
    // 文字雲
    const layout = d3.layout
      .cloud() 
      .size([cloudWidth, cloudHeight]) 
      .words(
        myWords.map(function (d, i) {
          return { text: d.text, size: d.size, index: i }
        }),
      )
      .padding(5) //space between words
      .rotate(function () {
        return 0
      })
      .fontSize(function (d) { //文字大小的調整
        return d.size * (14 - bankLength * 2)
      })
      .on('end', draw)
    // 文字雲start
    layout.start()
    
    // 畫出文字雲
    function draw(words) {
      svg
        .append('g')
        .attr('transform', 'translate(' + layout.size()[0] / 2 + ',' + layout.size()[1] / 2 + ')')
        .selectAll('text')
        .data(words)
        .enter()
        .append('text')
        .attr('font-size', function (d) {
          return d.size
        })
        .attr('fill', (d, i) => fill[d.index % 10])
        .attr('text-anchor', 'middle')
        .attr('font-family', 'Impact')
        .attr('transform', function (d) {
          return 'translate(' + [d.x, d.y] + ')rotate(' + d.rotate + ')'
        })
        .text(function (d) {
          return d.text
        })
        // 將資料綁在element上，要用在
        .attr('data-word', (d) => d.text)
        .attr('data-bank', filter.bank)
        .attr('data-dateStart', filter.dateStart)
        .attr('data-dateEnd', filter.dateEnd)
        .attr('class', 'cloudText cursor-pointer')
        .attr('data-color', (d, i) => fill[d.index % 10])
    }
    // 所有的文字增加效果和click事件
    d3.selectAll('text.cloudText')
      .on('mouseover', wordHighlight)
      .on('mouseleave', wordHighlight)
      .on('click', (event, d) => {
        // 調整詳細modal內容
        document.getElementById('bigram-body').innerHTML = ''
        document.getElementById('trigram-body').innerHTML = ''
        document.getElementById('sentence-list').innerHTML = ''
        const loading = `<div role="status" class="py-20" >
                  <img src="../static/img/SK_logo.png" alt="" class="animate-bounce w-40 mx-auto" />

                  <p class="text-center text-2xl animate-pulse">Loading...</p>
                </div>`
        document.getElementById('bigram-loading').innerHTML = loading
        document.getElementById('trigram-loading').innerHTML = loading
        document.getElementById('sentence-list').innerHTML = loading
        const element = event.target.dataset
        // 移除body的滾動條
        d3.select('body').classed('overflow-y-hidden	', true)
        // 移除modal的隱藏
        d3.select('#modal').classed('hidden', false).classed('opacity-100', true)
        // 填入相對文字
        d3.select('#modal-topic').text(element.bank)
        d3.select('#modal-keyword').text(element.word)
        d3.select('#modal-dateStart').text(element.dateStart)
        d3.select('#modal-dateEnd').text(element.dateEnd)
        let input = {
          type: filter.type,
          topic: element.bank,
          keyword: element.word,
          product: filter.product,
          source: filter.source,
          dateStart: element.dateStart,
          dateEnd: element.dateEnd,
          content: filter.content,
        }
        Ngram(input)
        sentence(input)
      })
  })
  // word highlight
  function wordHighlight(event, d) {
      // 滑鼠移進文字
    if (event.type === 'mouseover') {
      // 將全部的文字轉為灰色
      d3.selectAll('text.cloudText').transition().duration(500).attr('fill', 'gray')
      // 選擇的文字調成紅色和放大
      d3.selectAll(`text[data-word = ${d.text}]`)
        .transition()
        .duration(100)
        .attr('font-size', function (d) {
          return d.size * 1.2
        })
        .attr('fill', 'red')
      // 滑鼠移出文字
    } else if (event.type === 'mouseleave') {
      // 將顏色調整成原始的顏色
      d3.selectAll('text.cloudText')
        .transition()
        .duration(100)
        .attr('fill', (d, i) => {
          return fill[d.index % 10]
        })
        // 文字縮小
      d3.selectAll(`text[data-word = ${d.text}]`)
        .transition()
        .duration(100)
        .attr('font-size', function (d) {
          return d.size / 1.2
        })
        .attr('fill', (d, i, element) => {
          return fill[d.index % 10]
        })
    }
  }
}
export default wordCloud
