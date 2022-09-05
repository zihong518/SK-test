// api
const Request = axios.create({
  baseURL: '',
})

// User 相關的 api
export const getWordCloud = (data) => Request.get(`/getCloud?type=${data.type}&name=${data.bank}&dataProduct=${data.product}&dataSource=${data.source}&dateStart=${data.dateStart}&dateEnd=${data.dateEnd}&content=${data.content}`)
export const getWordCount = (data) => Request.get(`/getCount?type=${data.type}&name=${data.bank}&content=${data.content}&dataProduct=${data.product}&dataSource=${data.source}`)

export const getDateRange = (type) => Request.get(`/getDateRange?type=${type}`)
export const getWordProportion = (data) => Request.get(`/getProportion?type=${data.type}&keywordA=${data.keywordA}&keywordB=${data.keywordB}&content=${data.content}&dataProduct=${data.product}&dataSource=${data.source}`)
export const getSent = (data) => Request.get(`/getSent?type=${data.type}&name=${data.bank}&content=${data.content}&dataProduct=${data.product}&dataSource=${data.source}`)
export const getSentWord = (data) => Request.get(`/getSentWord?type=${data.type}&name=${data.bank}&content=${data.content}&dataProduct=${data.product}&dataSource=${data.source}`)
export const getSentDict = () => Request.get(`/getSentDict`)
export const getNgram = (data, n) => Request.get(`/getNgram?type=${data.type}&topic=${data.topic}&keyword=${data.keyword}&dateStart=${data.dateStart}&dateEnd=${data.dateEnd}&dataProduct=${data.product}&dataSource=${data.source}&content=${data.content}&n=${n}`)
export const getSentence = (data) => Request.get(`/getSentence?type=${data.type}&topic=${data.topic}&keyword=${data.keyword}&dateStart=${data.dateStart}&dateEnd=${data.dateEnd}&dataProduct=${data.product}&dataSource=${data.source}&content=${data.content}`)
