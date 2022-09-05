import { getNgram, getSentence } from './api.js'
const sentColor = [
  {
    sent: 'positive',
    color: '#d20000',
  },
  {
    sent: 'negative',
    color: '#0089d2',
  },
  {
    sent: 'neutral',
    color: '#515456',
  },
]
export function Ngram(filter) {
  getNgram(filter, 2).then((res) => {
    document.getElementById('bigram-loading').firstChild.remove()
    const data = res.data.slice(0, 10).map((x) => {
      const word = x.word.split(' ')
      return {
        wordA: word[0],
        wordB: word[1],
        count: x.counts,
      }
    })
    const tableContent = document.getElementById('bigram-body')
    let content = ''
    data.forEach((element) => {
      content += `
     <tr>
      <td>${element.wordA}</td>
      <td>${element.wordB}</td>
      <td>${element.count}</td>
    </tr>
    `
    })
    tableContent.innerHTML = content
  })
  getNgram(filter, 3).then((res) => {
    document.getElementById('trigram-loading').firstChild.remove()
    const data = res.data.slice(0, 10).map((x) => {
      const word = x.word.split(' ')
      return {
        wordA: word[0],
        wordB: word[1],
        wordC: word[2],
        count: x.counts,
      }
    })
    const tableContent = document.getElementById('trigram-body')
    let content = ''
    data.forEach((element) => {
      content += `
     <tr>
      <td>${element.wordA}</td>
      <td>${element.wordB}</td>
      <td>${element.wordC}</td>

      <td>${element.count}</td>
    </tr>
    `
    })
    tableContent.innerHTML = content
  })
}
export function sentence(filter) {
  getSentence(filter)
    .then((res) => {
      const data = res.data
      const sentenceList = document.getElementById('sentence-list')
      if (sentenceList) {
        while (sentenceList.firstChild) {
          sentenceList.removeChild(sentenceList.firstChild)
        }
      }

      let content = ''
      if (filter.type == 'App') {
        data.forEach((element) => {
          content += `
     <li class="my-2" style="color:${sentColor.filter((x) => x.sent === element.sent)[0].color} " data-type="sentence">
        ${element.sentence}
     </li>
    `
        })
      } else {
        data.forEach((element) => {
          content += `
     <li class="my-2 "  >
        <a href="${element.artUrl}" target="_blank" data-type="sentence" class="hover:brightness-150 duration-75	" style="color:${sentColor.filter((x) => x.sent === element.sent)[0].color}">
        ${element.sentence}
        </a>
     </li>
    `
        })
      }
      sentenceList.innerHTML = content
    })
    .then(() => {
      const sentenceLi = document.querySelectorAll('[data-type=sentence]')
      sentenceLi.forEach((x) => {
        x.innerHTML = x.innerHTML.replaceAll(filter.keyword.toLowerCase(), `<span class="text-main font-bold text-l">${filter.keyword}</span>`)
        x.innerHTML = x.innerHTML.replaceAll(filter.keyword.toUpperCase(), `<span class="text-main font-bold text-l">${filter.keyword}</span>`)
      })
    })
}

export function keywordNgram(filter, key) {
  getNgram(filter, 2).then((res) => {
    document.getElementById(`bigram-loading-${key}`).firstChild.remove()
    const data = res.data.slice(0, 10).map((x) => {
      const word = x.word.split(' ')
      return {
        wordA: word[0],
        wordB: word[1],
        count: x.counts,
      }
    })
    const tableContent = document.getElementById(`bigram-body-${key}`)
    let content = ''
    data.forEach((element) => {
      content += `
     <tr>
      <td>${element.wordA}</td>
      <td>${element.wordB}</td>
      <td>${element.count}</td>
    </tr>
    `
    })
    tableContent.innerHTML = content
  })
  getNgram(filter, 3).then((res) => {
    document.getElementById(`trigram-loading-${key}`).firstChild.remove()
    const data = res.data.slice(0, 10).map((x) => {
      const word = x.word.split(' ')
      return {
        wordA: word[0],
        wordB: word[1],
        wordC: word[2],
        count: x.counts,
      }
    })
    const tableContent = document.getElementById(`trigram-body-${key}`)
    let content = ''
    data.forEach((element) => {
      content += `
     <tr>
      <td>${element.wordA}</td>
      <td>${element.wordB}</td>
      <td>${element.wordC}</td>

      <td>${element.count}</td>
    </tr>
    `
    })
    tableContent.innerHTML = content
  })
}

export function keywordSentence(filter, key) {
  getSentence(filter).then((res) => {
    const data = res.data
    const sentenceList = document.getElementById(`sentence-list-${key}`)
    if (sentenceList) {
      while (sentenceList.firstChild) {
        sentenceList.removeChild(sentenceList.firstChild)
      }
    }
    let content = ''
    if (filter.type == 'App') {
      data.forEach((element) => {
        content += `
     <li class="my-2" data-type="sentence" class="hover:brightness-150 duration-75	" style="color:${sentColor.filter((x) => x.sent === element.sent)[0].color}">
        ${element.sentence}
     </li>
    `
      })
    } else {
      data.forEach((element) => {
        content += `
     <li class="my-2">
        <a href="${element.artUrl}" data-type="sentence" target="_blank" class="hover:brightness-150 duration-75	" style="color:${sentColor.filter((x) => x.sent === element.sent)[0].color}">
        ${element.sentence}
        </a>
     </li>
    `
      })
    }

    sentenceList.innerHTML = content
    const sentence = document.querySelectorAll('[data-type =sentence]')
    sentence.forEach((x) => {
      x.innerHTML = x.innerHTML.replaceAll(filter.keyword.toLowerCase(), `<span class="text-main font-bold text-l">${filter.keyword}</span>`)
      x.innerHTML = x.innerHTML.replaceAll(filter.keyword.toUpperCase(), `<span class="text-main font-bold text-l">${filter.keyword}</span>`)
    })
  })
}
