import lineChart from './linechart.js'
import wordCloud from './wordcloud.js'
import proportionChart from './proportionChart.js'
import sentChart from './sentChart.js'
import { getWordCount, getDateRange, getWordProportion, getSent } from './api.js'
import { sentence, keywordSentence } from './ngram.js'

const { createApp } = Vue
const loading = `<div role="status" class="py-20">
                <img src="../static/img/SK_logo.png" alt="" class="animate-bounce w-40 mx-auto " />

             <p class="text-center text-2xl animate-pulse">Loading...</p>
        </div>`
createApp({
  data() {
    return {
      typeChoose: [
        {
          value: '論壇',
          type: 'Forum',
          checked: true,
        },
        {
          value: 'app評論',
          type: 'App',
          checked: false,
        },
      ],
      controlPanel: [
        {
          type: 'typeForum',
          value: '論壇',
          list: [
            {
              filterTitle: '產品比較',
              model: 'creditcard',
              filterName: 'product',
              filterItems: [
                {
                  name: '信用卡',
                  value: 'creditcard',
                },
                {
                  name: '銀行服務',
                  value: 'Bank_Service',
                  // checked: true,
                },
              ],
            },
            {
              filterTitle: '篩選看板',
              filterName: 'source',
              model: ['PTT'],
              checkBox: true,
              filterItems: [
                {
                  name: 'PTT',
                  value: 'PTT',
                },
              ],
            },
            {
              filterTitle: '內容篩選',
              filterName: 'content',
              model: 'article-content',
              filterItems: [
                {
                  name: '全部',
                  value: 'all-content',
                },
                {
                  name: '主文',
                  value: 'article-content',
                },
                {
                  name: '留言',
                  value: 'review-content',
                },
              ],
            },
          ],
        },
        {
          type: 'typeApp',
          value: 'app評論',
          list: [
            {
              filterTitle: '產品比較',
              filterName: 'product',
              model: ['新光', '國泰', 'Richart'],
              checkBox: true,
              filterItems: [
                {
                  name: '新光',
                  value: '新光',
                },
                {
                  name: '國泰',
                  value: '國泰',
                },
                {
                  name: 'iLeo',
                  value: 'iLeo',
                },
                {
                  name: 'KoKo',
                  value: 'KoKo',
                },
                {
                  name: '台新',
                  value: '台新',
                },
                {
                  name: 'Richart',
                  value: 'Richart',
                },
                {
                  name: '永豐',
                  value: '永豐',
                },
                {
                  name: 'DAWHO',
                  value: 'DAWHO',
                },
              ],
            },
            {
              filterTitle: '篩選看板',
              filterName: 'source',
              model: ['app store', 'play store'],
              checkBox: true,
              filterItems: [
                {
                  name: 'App store',
                  value: 'app store',
                  checked: true,
                },
                {
                  name: 'Google play',
                  value: 'play store',
                  checked: true,
                },
              ],
            },
          ],
        },
      ],
      bankButton: [
        {
          name: '新光',
        },
        {
          name: '永豐',
        },
        {
          name: '台新',
        },
      ],

      dateButton: [
        {
          dateStart: '2022/04/01',
          dateEnd: '2022/05/01',
        },
        {
          dateStart: '2022/05/01',
          dateEnd: '2022/06/01',
        },
        {
          dateStart: '2022/06/01',
          dateEnd: '2022/07/01',
        },
      ],
      tabs: ['提及熱度比較', '文字雲比較', '使用字詞比較', '情緒分析'],
      currentTab: '提及熱度比較',
      keywordA: 'OU',
      keywordB: '寰宇',
      minDate: '',
      maxDate: '',
      currentType: 'Forum',
    }
  },
  methods: {
    chooseChange() {
      this.typeChoose[0].checked = !this.typeChoose[0].checked
      this.typeChoose[1].checked = !this.typeChoose[1].checked
      this.chooseList = function choose() {
        const choose = this.typeChoose.filter((item) => {
          return item.checked == true
          // return item.checked
        })[0].value

        return this.controlPanel.filter((item) => {
          // console.log(item.value)
          return item.value === choose
        })[0]
      }

      setTimeout(() => {
        if (this.currentType === 'App') {
          this.temp = this.bankButton
          let product = document.querySelectorAll('input[name=product]:checked')
          let temp = []
          product.forEach((x) => {
            temp.push({ name: x._value })
          })
          this.bankButton = temp
          this.keywordA = '新光'
          this.keywordB = '台新'
        } else {
          this.bankButton = this.temp
        }
        this.generateChart()
      }, 10)
      // setTimeout(() => {
      //   this.getSentChart()
      // }, 30)
    },
    generateChart() {
      this.getWordCloud()

      this.getLineChart()

      this.getWordProportion()

      this.getSentChart()
    },
    changeTab(tab) {
      this.currentTab = tab
    },
    getWordCloud() {
      let element = document.getElementById('canvas')
      if (element) {
        while (element.firstChild) {
          element.removeChild(element.firstChild)
        }
      }

      const type = document.querySelector('input[name=type]:checked').value
      const product = document.querySelector('input[name=product]:checked').value
      const source = document.querySelectorAll('input[name=source]:checked')
      const sourceList = [...source].map((x) => x.value).toString()
      let content = 'article-content'
      if (this.currentType === 'Forum') {
        content = document.querySelector('input[name=content]:checked').value
      }
      // console.log(type,product,sourceList,content);

      for (let i = 0; i < this.dateButton.length; i++) {
        for (let j = 0; j < this.bankButton.length; j++) {
          let data = {
            type: type,
            product: product,
            source: sourceList,
            content: content,
            bank: this.bankButton[j].name,
            dateGroup: 'dateGroup_' + i,
            bankGroup: 'bankGroup_' + i,
            id: 'bank_' + this.bankButton[j].name + '-' + i,
            dateStart: this.dateButton[i].dateStart,
            dateEnd: this.dateButton[i].dateEnd,
          }
          let bankLength = this.bankButton.length
          wordCloud(data, bankLength)
        }
      }
    },
    getLineChart() {
      let element = document.getElementById('lineChart')
      if (element) {
        while (element.firstChild) {
          element.removeChild(element.firstChild)
        }
      }

      const type = document.querySelector('input[name=type]:checked').value
      const product = document.querySelector('input[name=product]:checked').value
      const source = document.querySelectorAll('input[name=source]:checked')
      const sourceList = [...source].map((x) => x.value).toString()
      let content = 'article-content'
      if (this.currentType === 'Forum') {
        content = document.querySelector('input[name=content]:checked').value
      }
      // console.log(type,product,sourceList,content);
      const bank = this.bankButton.map((x) => x.name).toString()
      let filter = {
        type: type,
        product: product,
        source: sourceList,
        content: content,
        bank: bank,
      }

      document.getElementById('lineChart').innerHTML = loading
      getWordCount(filter)
        .then((res) => {
          this.lineChartData = res.data
          document.getElementById('lineChart').removeChild(document.getElementById('lineChart').firstChild)
          lineChart(res.data, filter)
        })
        .catch((err) => {
          console.log(err)
        })

      // let rawData = getData()
    },
    getWordProportion() {
      let element = document.getElementById('proportionChart')
      if (element) {
        while (element.firstChild) {
          element.removeChild(element.firstChild)
        }
      }
      element.innerHTML = loading
      const type = document.querySelector('input[name=type]:checked').value
      const product = document.querySelector('input[name=product]:checked').value
      const source = document.querySelectorAll('input[name=source]:checked')
      const sourceList = [...source].map((x) => x.value).toString()
      let content = 'article-content'
      if (this.currentType === 'Forum') {
        content = document.querySelector('input[name=content]:checked').value
      }
      const keywordA = this.keywordA
      const keywordB = this.keywordB
      let filter = {
        type: type,
        product: product,
        source: sourceList,
        content: content,
        keywordA: keywordA,
        keywordB: keywordB,
      }
      getWordProportion(filter)
        .then((res) => {
          element.removeChild(element.firstChild)

          proportionChart(res.data, filter)
        })
        .catch((err) => {
          console.log(err)
        })
    },
    getSentChart() {
      let element = document.getElementById('sentChart')
      if (element) {
        while (element.firstChild) {
          element.removeChild(element.firstChild)
        }
      }

      element.innerHTML = loading

      const type = document.querySelector('input[name=type]:checked').value
      const product = document.querySelector('input[name=product]:checked').value
      const source = document.querySelectorAll('input[name=source]:checked')
      const sourceList = [...source].map((x) => x.value).toString()
      let content = 'article-content'
      if (this.currentType === 'Forum') {
        content = document.querySelector('input[name=content]:checked').value
      }

      this.bankButton.forEach((bank) => {
        let filter = {
          type: type,
          product: product,
          source: sourceList,
          content: content,
          bank: bank.name,
          minDate: this.minDate,
          maxDate: this.maxDate,
        }
        getSent(filter)
          .then((res) => {
            sentChart(res.data, filter)
          })
          .catch((err) => {
            console.log(err)
          })
      })
      document.getElementById('sentChart').removeChild(document.getElementById('sentChart').firstChild)
    },
    bankSubmit(event) {
      let inputData = ''
      if (this.currentType == 'Forum') {
        inputData = document.getElementById('bankButtonInput').value
        if (inputData) {
          this.bankButton.push({
            name: inputData,
          })
        }
        const type = document.querySelector('input[name=type]:checked').value
        const product = document.querySelector('input[name=product]:checked').value
        const source = document.querySelectorAll('input[name=source]:checked')
        const sourceList = [...source].map((x) => x.value).toString()
        let content = 'article-content'
        if (this.currentType === 'Forum') {
          content = document.querySelector('input[name=content]:checked').value
        }
        let filter = {
          type: type,
          product: product,
          source: sourceList,
          content: content,
          bank: inputData,
          minDate: this.minDate,
          maxDate: this.maxDate,
        }
        getSent(filter)
          .then((res) => {
            sentChart(res.data, filter)
          })
          .catch((err) => {
            console.log(err)
          })
        this.getWordCloud()
        this.getLineChart()
      } else if (event.target.checked) {
        inputData = event.target.value
        this.bankButton.push({
          name: inputData,
        })
      } else {
        inputData = event.target.value
        this.removeBank(event)
      }
    },
    dateSubmit() {
      const dateStartValue = document.getElementById('dateStart').innerText
      const dateEndValue = document.getElementById('dateEnd').innerText
      if (new Date(dateStartValue) > new Date(dateEndValue)) {
        alert('日期錯誤')
      } else if (dateStartValue !== '' && dateEndValue !== '') {
        this.dateButton.push({
          dateStart: dateStartValue,
          dateEnd: dateEndValue,
        })
        this.getWordCloud()
      }
    },
    removeBank(element) {
      this.bankButton = this.bankButton.filter((x) => {
        return x.name != element.target.dataset.value
      })
      if (this.currentTab == '文字雲比較') {
        this.getWordCloud()
      }

      if (this.currentType === 'App') {
        const productCheckbox = document.querySelectorAll('input[name=product]:checked')
        console.log(productCheckbox)
        productCheckbox.forEach((x) => {
          x.checked = false
          if (x.value === element.target.dataset.value) {
            const modelList = this.controlPanel[1].list[0].model
            modelList.splice(modelList.indexOf(x.value), 1)
          }
        })
      }
      document.getElementById('sent' + element.target.dataset.value).remove()
      document.getElementById('title' + element.target.dataset.value).remove()
    },
    removeDate(index) {
      this.dateButton.splice(index, 1)
      this.getWordCloud()
    },
    dateRangeCreate() {
      const minDate = this.minDate
      const maxDate = this.maxDate
      const sliderRange = d3
        .sliderBottom()
        .min(minDate)
        .max(maxDate)
        .width(800)
        .fill('#D4011D')
        .tickFormat(d3.timeFormat('%Y/%m/%d'))
        .default([minDate, maxDate])
        .on('onchange', function (val) {
          d3.select(`#dateStart`).text(d3.timeFormat('%Y/%m/%d')(val[0]))
          d3.select(`#dateEnd`).text(d3.timeFormat('%Y/%m/%d')(val[1]))
        })
      d3.select('#dateRange').append('svg').attr('id', 'dateRangeSvg').attr('preserveAspectRatio', 'xMinYMin meet').attr('viewBox', '0 0 950 600').classed('svg-content', true).append('g').attr('transform', 'translate(80,30)').call(sliderRange)
      d3.selectAll('#dateRangeSvg  text').attr('font-size', '1.5em')
    },
    submitKeyword() {
      if (document.getElementById('keywordInputA').value) {
        this.keywordA = document.getElementById('keywordInputA').value
      }
      if (document.getElementById('keywordInputB').value) {
        this.keywordB = document.getElementById('keywordInputB').value
      }
      this.getWordProportion()
    },
    closeModal() {
      document.getElementById('modal').classList.add('hidden')
      document.getElementById('app').classList.remove('overflow-y-hidden')
      document.getElementById('proportionModal').classList.add('hidden')
    },
    randomPick() {
      const type = document.querySelector('input[name=type]:checked').value
      const product = document.querySelector('input[name=product]:checked').value
      const source = document.querySelectorAll('input[name=source]:checked')
      const sourceList = [...source].map((x) => x.value).toString()
      let content = 'article-content'
      if (this.currentType === 'Forum') {
        content = document.querySelector('input[name=content]:checked').value
      }

      document.getElementById('sentence-list').innerHTML = loading
      let input = {
        type: type,
        topic: document.getElementById('modal-topic').innerText,
        keyword: document.getElementById('modal-keyword').innerText,
        product: product,
        source: sourceList,
        dateStart: document.getElementById('modal-dateStart').innerText,
        dateEnd: document.getElementById('modal-dateEnd').innerText,
        content: content,
      }
      sentence(input)
    },
    propRandomPick(key) {
      const type = document.querySelector('input[name=type]:checked').value
      const product = document.querySelector('input[name=product]:checked').value
      const source = document.querySelectorAll('input[name=source]:checked')
      const sourceList = [...source].map((x) => x.value).toString()
      let content = 'article-content'
      if (this.currentType === 'Forum') {
        content = document.querySelector('input[name=content]:checked').value
      }

      document.getElementById(`sentence-list-${key}`).innerHTML = loading
      let input = {
        type: type,
        topic: document.getElementById(`modal-topic-${key}`).innerText,
        keyword: document.getElementById(`modal-keyword-${key}`).innerText,
        product: product,
        source: sourceList,
        dateStart: document.getElementById(`modal-dateStart-${key}`).innerText,
        dateEnd: document.getElementById(`modal-dateEnd-${key}`).innerText,
        content: content,
      }
      keywordSentence(input, key)
    },
  },
  computed: {
    chooseList: function choose() {
      const choose = this.typeChoose.filter((item) => {
        return item.checked == true
        // return item.checked
      })[0].value

      return this.controlPanel.filter((item) => {
        // console.log(item.value)
        return item.value === choose
      })[0]
    },
  },
  async mounted() {
    const choose = this.typeChoose.filter((item) => {
      return item.checked == true
      // return item.checked
    })[0].type
    await getDateRange(choose)
      .then((res) => {
        return res.data
      })
      .then((data) => {
        this.minDate = new Date(data.minDate)
        this.maxDate = new Date(data.maxDate)
      })

    this.dateRangeCreate()
    this.generateChart()
  },
  compilerOptions: {
    delimiters: ['[[', ']]'],
  },
}).mount('#app')
