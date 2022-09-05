import { getWordCloud } from './api.js'
import { Ngram, sentence } from './ngram.js'
function wordCloud(filter, bankLength) {
  const main = document.getElementById('canvas')
  const idName = filter.id

  if (!document.getElementById(filter.dateGroup)) {
    const group = document.createElement('div')
    group.setAttribute('id', filter.dateGroup)
    group.setAttribute('class', 'flex flex-col	')
    main.appendChild(group)
    const date = document.createElement('p')
    date.setAttribute('class', 'text-xl  mx-auto px-3 py-1 bg-green-100 rounded-md')
    date.innerText = filter.dateStart + '~' + filter.dateEnd
    group.appendChild(date)

    const bankGroup = document.createElement('div')
    bankGroup.setAttribute('id', filter.bankGroup)
    bankGroup.setAttribute('class', 'flex ')
    group.appendChild(bankGroup)
  }

  const canvas = document.createElement('div')
  canvas.setAttribute('id', idName)

  const group = document.getElementById(filter.bankGroup)
  group.appendChild(canvas)

  const fill = d3.schemeCategory10

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

  const selectSizeFactor = function (min, max, value) {
    const a = (max - min) / (10 - 1)
    const b = max - a * 10
    return (value - b) / a
  }
  // myWords = tokenize(test)
  const canvasWidth = (document.body.clientWidth * 5) / 6 - 100
  const cloudWidth = canvasWidth / bankLength
  const cloudHeight = (cloudWidth * 3) / 4

  const margin = { top: 10, right: 10, bottom: 10, left: 10 },
    width = 600 - margin.left - margin.right,
    height = 450 - margin.top - margin.bottom

  const svg = d3
    .select('#' + idName)
    .append('svg')
    .attr('width', cloudWidth + 10)
    .attr('height', cloudHeight + margin.top + margin.bottom)
    .attr('id', 'wordCloudSvg')
    .attr('class', 'mx-auto')
    .append('g')
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')

  d3.select('#' + idName)
    .append('p')
    .attr('class', 'text-center text-xl mb-5')
    .text(filter.bank)

  getWordCloud(filter).then((data) => {
    // console.log(data.data)
    let myWords = []
    data.data.map((x) => {
      myWords.push({
        text: x._id,
        size: x.wordCount,
      })
    })

    myWords = tokenize(myWords)
    myWords = myWords.sort((a, b) => b.size - a.size)
    myWords = myWords.slice(0, 50)
    // console.log(myWords);
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
      .fontSize(function (d) {
        return d.size * (14 - bankLength * 2)
      })
      .on('end', draw)

    layout.start()

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
        .attr('data-word', (d) => d.text)
        .attr('data-bank', filter.bank)
        .attr('data-dateStart', filter.dateStart)
        .attr('data-dateEnd', filter.dateEnd)
        .attr('class', 'cloudText cursor-pointer')
        .attr('data-color', (d, i) => fill[d.index % 10])
    }
    function test(input) {
      console.log('test')
      sentence(input)
    }
    d3.selectAll('text.cloudText')
      .on('mouseover', wordHighlight)
      .on('mouseleave', wordHighlight)
      .on('click', (event, d) => {
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
        d3.select('body').classed('overflow-y-hidden	', true)
        d3.select('#modal').classed('hidden', false).classed('opacity-100', true)
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

  function wordHighlight(event, d) {
    if (event.type === 'mouseover') {
      d3.selectAll('text.cloudText').transition().duration(500).attr('fill', 'gray')
      d3.selectAll(`text[data-word = ${d.text}]`)
        .transition()
        .duration(100)
        .attr('font-size', function (d) {
          return d.size * 1.2
        })
        .attr('fill', 'red')

      d3.select('#' + idName)
        .append('p')
        .attr('class', 'text-center text-xl mb-5')
    } else if (event.type === 'mouseleave') {
      d3.selectAll('text.cloudText')
        .transition()
        .duration(100)
        .attr('fill', (d, i, element) => {
          return fill[d.index % 10]
        })
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
