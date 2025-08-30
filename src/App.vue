<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useTheme } from 'vuetify'

const theme = useTheme()

const stores = ref([])
const searchQuery = ref('')
const selectedCategory = ref('전체')
const selectedSubCategory = ref('전체')
const favorites = ref(JSON.parse(localStorage.getItem('favorites') || '[]'))
const currentPage = ref(1)
const itemsPerPage = ref(24)
const isLoading = ref(true)
const searchTimeout = ref(null)
const isDark = ref(localStorage.getItem('darkMode') === 'true')
const selectedStore = ref(null)
const showStoreModal = ref(false)
const userLocation = ref(null)
const locationError = ref('')
const isLocationLoading = ref(false)
const sortBy = ref('default') // 'default', 'distance', 'name'

const categories = ['전체', '서울', '부산', '대구', '인천', '광주', '대전', '울산', '경기도', '강원도', '충청도', '전라도', '경상도', '제주도']
const storeTypes = ['전체', '인형뽑기', '크레인', '게임센터', '오락실', '게임존', '플레이존', '토이']

const subCategories = computed(() => {
  if (selectedCategory.value === '서울') {
    return ['전체', '강남구', '서초구', '마포구', '중구', '종로구', '강북구', '성북구', '동대문구', '서대문구', 
           '관악구', '동작구', '영등포구', '구로구', '금천구', '양천구', '강서구', '노원구', '도봉구', '성동구', 
           '광진구', '중랑구', '은평구', '송파구', '강동구']
  } else if (selectedCategory.value === '부산') {
    return ['전체', '해운대구', '부산진구', '동래구', '남구', '서구', '사하구', '금정구', '연제구', 
           '수영구', '사상구', '북구', '강서구', '중구', '영도구', '기장군']
  } else if (selectedCategory.value === '대구') {
    return ['전체', '중구', '동구', '서구', '남구', '북구', '수성구', '달서구', '달성군']
  } else if (selectedCategory.value === '인천') {
    return ['전체', '중구', '동구', '미추홀구', '연수구', '남동구', '부평구', '계양구', '서구', '강화군', '옹진군']
  } else if (selectedCategory.value === '경기도') {
    return ['전체', '수원시', '성남시', '고양시', '용인시', '부천시', '안산시', '안양시', '남양주시', '화성시', 
           '평택시', '의정부시', '시흥시', '파주시', '김포시', '광명시', '광주시', '군포시', '하남시', '오산시', 
           '양주시', '구리시', '안성시', '포천시', '의왕시', '여주시', '동두천시', '과천시', '가평군', '연천군']
  }
  return ['전체']
})

const filteredStores = computed(() => {
  let filtered = stores.value

  // 대분류 필터 (시/도) - 최적화
  if (selectedCategory.value !== '전체') {
    const categoryFilter = selectedCategory.value
    filtered = filtered.filter(store => store.address.includes(categoryFilter))
  }

  // 소분류 필터 (구/시) - 최적화  
  if (selectedSubCategory.value !== '전체') {
    const subCategoryFilter = selectedSubCategory.value
    filtered = filtered.filter(store => store.address.includes(subCategoryFilter))
  }

  // 검색 필터 - 디바운싱 적용
  if (searchQuery.value && searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(store => 
      store.name && store.address &&
      (store.name.toLowerCase().includes(query) ||
       store.address.toLowerCase().includes(query))
    )
  }

  return filtered
})

// 정렬된 스토어 리스트
const sortedStores = computed(() => {
  let sorted = [...filteredStores.value]

  if (sortBy.value === 'distance' && userLocation.value) {
    // 거리순 정렬
    sorted = sorted.map(store => {
      const storeCoords = getCoordinatesFromAddress(store.address)
      const distance = calculateDistance(
        userLocation.value.lat, userLocation.value.lng,
        storeCoords.lat, storeCoords.lng
      )
      return { ...store, distance }
    }).sort((a, b) => a.distance - b.distance)
  } else if (sortBy.value === 'name') {
    // 가나다순 정렬
    sorted = sorted.sort((a, b) => a.name.localeCompare(b.name))
  }
  // 기본값은 원래 순서 유지

  return sorted
})

// 페이지네이션된 결과
const paginatedStores = computed(() => {
  const stores = sortedStores.value || []
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return stores.slice(start, end)
})

// 총 페이지 수
const totalPages = computed(() => {
  const length = sortedStores.value?.length || 0
  return Math.ceil(length / itemsPerPage.value)
})

// 검색 디바운싱
const debouncedSearch = (newQuery) => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  searchTimeout.value = setTimeout(() => {
    currentPage.value = 1 // 검색시 첫 페이지로
  }, 300)
}

// 검색어 변경 감지
watch(searchQuery, debouncedSearch)

// 필터 변경시 첫 페이지로
watch([selectedCategory, selectedSubCategory], () => {
  currentPage.value = 1
})

// 카테고리 변경시 서브카테고리 초기화
const onCategoryChange = () => {
  selectedSubCategory.value = '전체'
}

const toggleFavorite = (storeId) => {
  const index = favorites.value.indexOf(storeId)
  if (index > -1) {
    favorites.value.splice(index, 1)
  } else {
    favorites.value.push(storeId)
  }
  localStorage.setItem('favorites', JSON.stringify(favorites.value))
}

const isFavorite = (storeId) => {
  return favorites.value.includes(storeId)
}

const openMap = (url) => {
  window.open(url, '_blank')
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  theme.global.name.value = isDark.value ? 'dark' : 'light'
  localStorage.setItem('darkMode', isDark.value.toString())
}

const openStoreModal = (store) => {
  selectedStore.value = store
  showStoreModal.value = true
}

const closeStoreModal = () => {
  showStoreModal.value = false
  selectedStore.value = null
}

const shareStore = (store) => {
  if (navigator.share) {
    navigator.share({
      title: store.name,
      text: `${store.name} - ${store.address}`,
      url: window.location.href
    })
  } else {
    // 폴백: 클립보드에 복사
    navigator.clipboard.writeText(`${store.name} - ${store.address} - ${window.location.href}`)
  }
}

// 두 지점 간의 거리 계산 (Haversine formula)
const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371 // 지구 반지름 (km)
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
  return R * c
}

// 주소를 좌표로 변환 (상세 지역별 좌표)
const getCoordinatesFromAddress = (address) => {
  // 상세 지역별 좌표 (구/군 단위까지)
  const detailedCoords = {
    // 서울특별시 구별 좌표
    '강남구': { lat: 37.5173, lng: 127.0473 },
    '강동구': { lat: 37.5301, lng: 127.1238 },
    '강북구': { lat: 37.6393, lng: 127.0255 },
    '강서구': { lat: 37.5509, lng: 126.8495 },
    '관악구': { lat: 37.4784, lng: 126.9516 },
    '광진구': { lat: 37.5384, lng: 127.0822 },
    '구로구': { lat: 37.4954, lng: 126.8874 },
    '금천구': { lat: 37.4563, lng: 126.8956 },
    '노원구': { lat: 37.6542, lng: 127.0568 },
    '도봉구': { lat: 37.6688, lng: 127.0471 },
    '동대문구': { lat: 37.5744, lng: 127.0396 },
    '동작구': { lat: 37.5124, lng: 126.9393 },
    '마포구': { lat: 37.5663, lng: 126.9019 },
    '서대문구': { lat: 37.5794, lng: 126.9368 },
    '서초구': { lat: 37.4836, lng: 127.0327 },
    '성동구': { lat: 37.5635, lng: 127.0369 },
    '성북구': { lat: 37.5894, lng: 127.0167 },
    '송파구': { lat: 37.5145, lng: 127.1059 },
    '양천구': { lat: 37.5169, lng: 126.8664 },
    '영등포구': { lat: 37.5264, lng: 126.8962 },
    '용산구': { lat: 37.5322, lng: 126.9904 },
    '은평구': { lat: 37.6026, lng: 126.9291 },
    '종로구': { lat: 37.5735, lng: 126.9788 },
    '중구': { lat: 37.5641, lng: 126.9979 },
    '중랑구': { lat: 37.6063, lng: 127.0925 },
    
    // 경기도 주요 시/군
    '화성시': { lat: 37.1994, lng: 126.8311 },
    '고양시': { lat: 37.6584, lng: 126.8320 },
    '수원시': { lat: 37.2636, lng: 127.0286 },
    '부천시': { lat: 37.5035, lng: 126.7660 },
    '평택시': { lat: 36.9923, lng: 127.1127 },
    '시흥시': { lat: 37.3803, lng: 126.8028 },
    '용인시': { lat: 37.2411, lng: 127.1776 },
    '성남시': { lat: 37.4449, lng: 127.1388 },
    '안산시': { lat: 37.3236, lng: 126.8219 },
    '안양시': { lat: 37.3943, lng: 126.9568 },
    '남양주시': { lat: 37.6360, lng: 127.2167 },
    '의정부시': { lat: 37.7380, lng: 127.0340 },
    
    // 충청남도
    '천안시': { lat: 36.8151, lng: 127.1139 },
    '아산시': { lat: 36.7898, lng: 127.0016 },
    
    // 충청북도
    '청주시': { lat: 36.6424, lng: 127.4890 },
    
    // 경상남도
    '창원시': { lat: 35.2276, lng: 128.6811 },
    
    // 기본 시/도 좌표
    '서울': { lat: 37.5665, lng: 126.9780 },
    '부산': { lat: 35.1796, lng: 129.0756 },
    '대구': { lat: 35.8714, lng: 128.6014 },
    '인천': { lat: 37.4563, lng: 126.7052 },
    '광주': { lat: 35.1595, lng: 126.8526 },
    '대전': { lat: 36.3504, lng: 127.3845 },
    '울산': { lat: 35.5384, lng: 129.3114 }
  }

  // 상세 지역명 우선 검색 (구/군 단위)
  for (const region in detailedCoords) {
    if (address.includes(region)) {
      return detailedCoords[region]
    }
  }

  // 기본값 (서울)
  return detailedCoords['서울']
}

// 사용자 위치 가져오기
const getCurrentLocation = async () => {
  if (!navigator.geolocation) {
    locationError.value = '위치 서비스를 지원하지 않는 브라우저입니다.'
    return
  }

  isLocationLoading.value = true
  locationError.value = ''

  try {
    const position = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5분
      })
    })

    userLocation.value = {
      lat: position.coords.latitude,
      lng: position.coords.longitude
    }

    console.log('위치 획득 성공:', userLocation.value)
    console.log('거리순 정렬 모드 활성화')

    // 거리순 정렬로 자동 변경
    sortBy.value = 'distance'

  } catch (error) {
    locationError.value = '위치를 가져올 수 없습니다. 위치 권한을 허용해주세요.'
    console.error('위치 오류:', error)
  } finally {
    isLocationLoading.value = false
  }
}

onMounted(async () => {
  try {
    isLoading.value = true
    const response = await fetch(`${import.meta.env.BASE_URL}stores.json`)
    const data = await response.json()
    
    // 대용량 데이터를 청크 단위로 로드
    await nextTick()
    stores.value = data
    
    console.log(`총 ${data.length}개 매장 데이터 로드 완료`)
  } catch (error) {
    console.error('가게 데이터를 불러올 수 없습니다:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <v-app>
    <v-app-bar :color="isDark ? 'grey-darken-4' : 'deep-purple'" dark prominent>
      <v-app-bar-title>
        <v-icon class="mr-2">mdi-crane</v-icon>
        인형뽑기 가게 지도
      </v-app-bar-title>
      <template #append>
        <v-btn
          :icon="isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
          @click="toggleTheme"
          class="mr-2"
        ></v-btn>
        <v-btn
          :icon="isLocationLoading ? 'mdi-loading' : 'mdi-crosshairs-gps'"
          :class="{ 'mdi-spin': isLocationLoading }"
          @click="getCurrentLocation"
          :color="userLocation ? 'success' : 'default'"
          class="mr-2"
          :disabled="isLocationLoading"
        ></v-btn>
        <v-chip 
          class="ma-2" 
          :color="isDark ? 'grey-darken-2' : 'white'" 
          :text-color="isDark ? 'white' : 'deep-purple'"
        >
          {{ (sortedStores?.length || 0).toLocaleString() }}개 매장
        </v-chip>
      </template>
    </v-app-bar>

    <v-main>
      <v-container fluid class="pa-4">
        <!-- 위치 권한 거부 알림 배너 -->
        <v-alert
          v-if="locationError && sortBy === 'distance'"
          type="warning"
          variant="tonal"
          dismissible
          class="mb-4"
          title="위치 정보 접근이 제한됨"
          text="거리순 정렬을 위해서는 위치 정보 접근 권한이 필요합니다. 브라우저 설정에서 위치 권한을 허용해 주세요."
          @input="locationError = null"
        >
          <template #prepend>
            <v-icon>mdi-map-marker-alert</v-icon>
          </template>
          <template #append>
            <v-btn 
              size="small" 
              variant="text" 
              @click="sortBy = 'default'; locationError = null"
            >
              기본순으로 보기
            </v-btn>
          </template>
        </v-alert>
        <!-- 검색 및 필터 섹션 -->
        <v-card class="mb-4" elevation="2">
          <v-card-text>
            <v-row>
              <v-col cols="12" md="3">
                <v-text-field
                  v-model="searchQuery"
                  label="🔍 가게명 또는 주소 검색"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  clearable
                  hide-details
                  density="comfortable"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="selectedCategory"
                  :items="categories"
                  label="📍 시/도 선택"
                  prepend-inner-icon="mdi-map-marker"
                  variant="outlined"
                  hide-details
                  density="comfortable"
                  @update:modelValue="onCategoryChange"
                ></v-select>
              </v-col>
              <v-col cols="12" md="3" v-if="selectedCategory !== '전체'">
                <v-select
                  v-model="selectedSubCategory"
                  :items="subCategories"
                  :label="`🏛️ ${selectedCategory === '경기도' ? '시/군' : '구/군'} 선택`"
                  prepend-inner-icon="mdi-map-marker-outline"
                  variant="outlined"
                  hide-details
                  density="comfortable"
                ></v-select>
              </v-col>
              <v-col cols="12" :md="selectedCategory !== '전체' ? 3 : 6">
                <v-select
                  v-model="sortBy"
                  :items="[
                    { value: 'default', title: '기본순' },
                    { value: 'distance', title: '거리순', disabled: !userLocation },
                    { value: 'name', title: '가나다순' }
                  ]"
                  label="📊 정렬 방식"
                  prepend-inner-icon="mdi-sort"
                  variant="outlined"
                  hide-details
                  density="comfortable"
                ></v-select>
              </v-col>
            </v-row>
            
            <!-- 선택된 필터 표시 -->
            <v-row v-if="selectedCategory !== '전체' || selectedSubCategory !== '전체' || searchQuery" class="mt-2">
              <v-col cols="12">
                <div class="d-flex flex-wrap ga-2">
                  <v-chip 
                    v-if="selectedCategory !== '전체'"
                    closable
                    :color="isDark ? 'blue-grey-darken-1' : 'primary'"
                    :variant="isDark ? 'outlined' : 'flat'"
                    size="small"
                    @click:close="selectedCategory = '전체'; onCategoryChange()"
                  >
                    {{ selectedCategory }}
                  </v-chip>
                  <v-chip 
                    v-if="selectedSubCategory !== '전체'"
                    closable
                    :color="isDark ? 'blue-grey-darken-1' : 'secondary'"
                    :variant="isDark ? 'outlined' : 'flat'"
                    size="small"
                    @click:close="selectedSubCategory = '전체'"
                  >
                    {{ selectedSubCategory }}
                  </v-chip>
                  <v-chip 
                    v-if="searchQuery"
                    closable
                    :color="isDark ? 'green-darken-1' : 'success'"
                    :variant="isDark ? 'outlined' : 'flat'"
                    size="small"
                    @click:close="searchQuery = ''"
                  >
                    "{{ searchQuery }}"
                  </v-chip>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>

        <!-- 로딩 상태 -->
        <v-row v-if="isLoading">
          <v-col cols="12">
            <v-card class="text-center pa-8">
              <v-progress-circular
                indeterminate
                color="primary"
                size="64"
              ></v-progress-circular>
              <h3 class="text-h5 mt-4">데이터를 불러오는 중...</h3>
              <p class="text-body-2">잠시만 기다려주세요</p>
            </v-card>
          </v-col>
        </v-row>

        <!-- 매장 카드 목록 (페이지네이션) -->
        <v-row v-else>
          <v-col
            v-for="store in paginatedStores"
            :key="store.id"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <v-card class="store-card" elevation="3" @click="openStoreModal(store)">
              <v-card-title class="d-flex justify-space-between align-center">
                <span class="text-h6">{{ store.name }}</span>
                <v-btn
                  :icon="isFavorite(store.id) ? 'mdi-heart' : 'mdi-heart-outline'"
                  :color="isFavorite(store.id) ? 'pink' : 'grey'"
                  size="small"
                  variant="text"
                  @click.stop="toggleFavorite(store.id)"
                ></v-btn>
              </v-card-title>
              
              <v-card-text>
                <v-chip
                  prepend-icon="mdi-map-marker"
                  variant="tonal"
                  size="small"
                  color="primary"
                  class="mb-3"
                  style="width: 100%;"
                >
                  {{ store.address }}
                </v-chip>
                
                <!-- 거리 표시 (거리순 정렬 시에만) -->
                <div v-if="sortBy === 'distance' && store.distance !== undefined" class="d-flex align-center mb-2">
                  <v-icon color="success" size="small" class="mr-1">mdi-map-marker-distance</v-icon>
                  <span class="text-caption text-success font-weight-medium">
                    약 {{ store.distance.toFixed(1) }}km
                  </span>
                </div>
              </v-card-text>
              
              <v-card-actions class="pt-0">
                <v-btn
                  color="error"
                  variant="outlined"
                  size="small"
                  prepend-icon="mdi-google"
                  @click.stop="openMap(store.google_map)"
                  block
                  class="mb-2"
                >
                  구글 지도
                </v-btn>
              </v-card-actions>
              
              <v-card-actions class="pt-0">
                <v-btn
                  color="success"
                  variant="outlined"
                  size="small"
                  prepend-icon="mdi-map"
                  @click.stop="openMap(store.naver_map)"
                  block
                >
                  네이버 지도
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>

        <!-- 페이지네이션 -->
        <v-row v-if="!isLoading && (filteredStores?.length || 0) > 0 && totalPages > 1">
          <v-col cols="12">
            <v-card class="pa-4" elevation="1">
              <div class="d-flex justify-center align-center">
                <v-pagination
                  v-model="currentPage"
                  :length="totalPages"
                  :total-visible="7"
                  color="primary"
                  class="mb-2"
                ></v-pagination>
              </div>
              <div class="text-center">
                <v-chip variant="outlined" size="small">
                  {{ ((currentPage - 1) * itemsPerPage + 1).toLocaleString() }} - 
                  {{ Math.min(currentPage * itemsPerPage, filteredStores?.length || 0).toLocaleString() }} / 
                  {{ (filteredStores?.length || 0).toLocaleString() }}개 매장
                </v-chip>
              </div>
            </v-card>
          </v-col>
        </v-row>

        <!-- 검색 결과 없음 -->
        <v-row v-if="!isLoading && (filteredStores?.length || 0) === 0">
          <v-col cols="12">
            <v-card class="text-center pa-8" elevation="2">
              <v-icon size="64" class="mb-4" color="grey">mdi-magnify-remove</v-icon>
              <h3 class="text-h5 mb-2">검색 결과가 없습니다</h3>
              <p class="text-body-1 text-grey">다른 검색어를 사용하거나 필터를 초기화해보세요</p>
              <v-btn 
                color="primary" 
                variant="outlined" 
                @click="searchQuery = ''; selectedCategory = '전체'; selectedSubCategory = '전체'"
                class="mt-4"
              >
                필터 초기화
              </v-btn>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <!-- 매장 상세 모달 -->
    <v-dialog v-model="showStoreModal" max-width="600px">
      <v-card v-if="selectedStore" :class="isDark ? 'bg-grey-darken-4' : ''">
        <v-card-title class="d-flex justify-space-between align-center modal-title">
          <span class="text-h5">{{ selectedStore.name }}</span>
          <v-btn icon="mdi-close" @click="closeStoreModal"></v-btn>
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <v-chip
                prepend-icon="mdi-map-marker"
                size="large"
                color="primary"
                variant="tonal"
                class="mb-4"
                style="width: 100%;"
              >
                {{ selectedStore.address }}
              </v-chip>
            </v-col>
            
            
            <v-col cols="12">
              <v-alert
                type="info"
                variant="tonal"
                class="mb-4"
              >
                <v-icon>mdi-information</v-icon>
                <span class="ml-2">아래 버튼을 클릭하여 지도에서 정확한 위치를 확인하세요</span>
              </v-alert>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions class="pa-4">
          <v-btn
            color="error"
            variant="flat"
            prepend-icon="mdi-google"
            @click="openMap(selectedStore.google_map)"
            class="flex-grow-1 mr-2"
          >
            구글 지도 열기
          </v-btn>
          
          <v-btn
            color="success"
            variant="flat"
            prepend-icon="mdi-map"
            @click="openMap(selectedStore.naver_map)"
            class="flex-grow-1 ml-2"
          >
            네이버 지도 열기
          </v-btn>
        </v-card-actions>
        
        <v-card-actions class="pa-4 pt-0">
          <v-btn
            color="primary"
            variant="outlined"
            prepend-icon="mdi-heart"
            @click="toggleFavorite(selectedStore.id)"
            class="flex-grow-1 mr-2"
          >
            {{ isFavorite(selectedStore.id) ? '즐겨찾기 제거' : '즐겨찾기 추가' }}
          </v-btn>
          
          <v-btn
            color="secondary"
            variant="outlined"
            prepend-icon="mdi-share"
            @click="shareStore(selectedStore)"
            class="flex-grow-1 ml-2"
          >
            공유하기
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<style scoped>
.v-main {
  min-height: 100vh;
  transition: background 0.3s ease;
}

/* 라이트 모드 배경 */
.v-theme--light .v-main {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 다크 모드 배경 */  
.v-theme--dark .v-main {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.store-card {
  transition: all 0.3s ease;
  border-radius: 12px !important;
  height: 100%;
  cursor: pointer;
}

/* 라이트 모드 카드 호버 */
.v-theme--light .store-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
  border: 2px solid rgba(102, 126, 234, 0.3);
}

/* 다크 모드 카드 호버 */
.v-theme--dark .store-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255,255,255,0.1) !important;
  border: 2px solid rgba(102, 126, 234, 0.5);
}

/* 라이트 모드 카드 타이틀 */
.v-theme--light .v-card-title {
  background: linear-gradient(45deg, #667eea, #764ba2) !important;
  color: white !important;
  font-weight: bold;
}

/* 다크 모드 카드 타이틀 */
.v-theme--dark .v-card-title {
  background: linear-gradient(45deg, #4a5568, #2d3748) !important;
  color: #e2e8f0 !important;
  font-weight: bold;
}

/* 모달 타이틀 스타일 */
.modal-title {
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.v-theme--dark .modal-title {
  background: linear-gradient(45deg, #374151, #1f2937) !important;
  color: #f9fafb !important;
}

.v-btn {
  font-weight: 500;
  text-transform: none !important;
  border-radius: 8px !important;
}

.v-btn:hover {
  transform: translateY(-1px);
}

.v-chip {
  font-weight: 500;
}

/* 필터 카드 스타일 - 라이트 모드 */
.v-theme--light .v-card:not(.store-card) {
  background: rgba(255,255,255,0.95) !important;
  backdrop-filter: blur(10px);
}

/* 필터 카드 스타일 - 다크 모드 */
.v-theme--dark .v-card:not(.store-card) {
  background: rgba(30,30,46,0.95) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.1);
}

/* 반응형 디자인 */
@media (max-width: 960px) {
  .v-col[cols="12"][md="4"] {
    margin-bottom: 8px;
  }
}

@media (max-width: 600px) {
  .v-app-bar-title {
    font-size: 1.1rem;
  }
  
  .v-chip {
    font-size: 0.875rem;
  }
}

/* 애니메이션 */
.v-card-actions .v-btn {
  transition: all 0.2s ease;
}

.v-card-actions .v-btn:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

/* 스크롤바 커스터마이징 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(255,255,255,0.1);
}

::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.3);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.5);
}
</style>
