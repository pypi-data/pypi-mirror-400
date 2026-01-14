/**
 * Data catalog page translations.
 *
 * Contains translations for the data catalog management page.
 */
import { t, type Dictionary } from 'intlayer'

const catalogContent = {
  key: 'catalog',
  content: {
    // Page titles
    title: t({ en: 'Data Catalog', ko: '데이터 카탈로그' }),
    subtitle: t({
      en: 'Browse and manage data assets',
      ko: '데이터 자산 탐색 및 관리',
    }),
    assets: t({ en: 'Assets', ko: '자산' }),

    // Actions
    addAsset: t({ en: 'Add Asset', ko: '자산 추가' }),
    editAsset: t({ en: 'Edit Asset', ko: '자산 수정' }),
    deleteAsset: t({ en: 'Delete Asset', ko: '자산 삭제' }),
    addColumn: t({ en: 'Add Column', ko: '컬럼 추가' }),
    addTag: t({ en: 'Add Tag', ko: '태그 추가' }),

    // Form fields
    assetName: t({ en: 'Asset Name', ko: '자산명' }),
    assetType: t({ en: 'Asset Type', ko: '자산 유형' }),
    dataSource: t({ en: 'Data Source', ko: '데이터 소스' }),
    columns: t({ en: 'Columns', ko: '컬럼' }),
    qualityScore: t({ en: 'Quality Score', ko: '품질 점수' }),
    tags: t({ en: 'Tags', ko: '태그' }),
    description: t({ en: 'Description', ko: '설명' }),
    owner: t({ en: 'Owner', ko: '담당자' }),
    selectSource: t({ en: 'Select data source', ko: '데이터 소스 선택' }),
    noSource: t({ en: 'No data source', ko: '데이터 소스 없음' }),

    // Asset types
    assetTypes: {
      table: t({ en: 'Table', ko: '테이블' }),
      file: t({ en: 'File', ko: '파일' }),
      api: t({ en: 'API', ko: 'API' }),
    },

    // Column fields
    columnName: t({ en: 'Column Name', ko: '컬럼명' }),
    dataType: t({ en: 'Data Type', ko: '데이터 타입' }),
    nullable: t({ en: 'Nullable', ko: 'Null 허용' }),
    primaryKey: t({ en: 'Primary Key', ko: '기본키' }),
    mappedTerm: t({ en: 'Mapped Term', ko: '매핑된 용어' }),

    // Column mapping
    columnMapping: t({ en: 'Column Mapping', ko: '컬럼 매핑' }),
    mapToTerm: t({ en: 'Map to Term', ko: '용어에 매핑' }),
    unmapTerm: t({ en: 'Remove Mapping', ko: '매핑 해제' }),
    searchTermToMap: t({ en: 'Search terms to map...', ko: '매핑할 용어 검색...' }),
    noTermSelected: t({ en: 'No term mapped', ko: '매핑된 용어 없음' }),

    // Tags
    tagName: t({ en: 'Tag Name', ko: '태그명' }),
    tagValue: t({ en: 'Tag Value', ko: '태그 값' }),
    noTags: t({ en: 'No tags', ko: '태그 없음' }),

    // Sensitivity
    sensitivity: {
      title: t({ en: 'Sensitivity', ko: '민감도' }),
      public: t({ en: 'Public', ko: '공개' }),
      internal: t({ en: 'Internal', ko: '내부용' }),
      confidential: t({ en: 'Confidential', ko: '기밀' }),
      restricted: t({ en: 'Restricted', ko: '제한' }),
    },

    // Search & Filter
    searchAssets: t({ en: 'Search assets...', ko: '자산 검색...' }),
    filterByType: t({ en: 'Filter by type', ko: '유형 필터' }),
    filterBySource: t({ en: 'Filter by source', ko: '소스 필터' }),
    allTypes: t({ en: 'All types', ko: '모든 유형' }),
    allSources: t({ en: 'All sources', ko: '모든 소스' }),

    // Empty states
    noAssets: t({ en: 'No assets found', ko: '자산이 없습니다' }),
    noAssetsYet: t({ en: 'No assets yet', ko: '등록된 자산이 없습니다' }),
    noAssetsDesc: t({
      en: 'Add your first data asset to start building your catalog',
      ko: '첫 번째 데이터 자산을 추가하여 카탈로그를 구축하세요',
    }),
    addFirstAsset: t({ en: 'Add Your First Asset', ko: '첫 번째 자산 추가' }),
    noColumns: t({ en: 'No columns defined', ko: '정의된 컬럼이 없습니다' }),

    // Confirmation
    confirmDelete: t({
      en: 'Are you sure you want to delete this asset? All columns and tags will also be deleted.',
      ko: '이 자산을 삭제하시겠습니까? 모든 컬럼과 태그도 함께 삭제됩니다.',
    }),

    // Messages
    loadError: t({ en: 'Failed to load assets', ko: '자산을 불러오지 못했습니다' }),
    createSuccess: t({ en: 'Asset created successfully', ko: '자산이 생성되었습니다' }),
    createError: t({ en: 'Failed to create asset', ko: '자산 생성에 실패했습니다' }),
    updateSuccess: t({ en: 'Asset updated successfully', ko: '자산이 수정되었습니다' }),
    updateError: t({ en: 'Failed to update asset', ko: '자산 수정에 실패했습니다' }),
    deleteSuccess: t({ en: 'Asset deleted successfully', ko: '자산이 삭제되었습니다' }),
    deleteError: t({ en: 'Failed to delete asset', ko: '자산 삭제에 실패했습니다' }),
    mappingSuccess: t({ en: 'Column mapped successfully', ko: '컬럼이 매핑되었습니다' }),
    mappingError: t({ en: 'Failed to map column', ko: '컬럼 매핑에 실패했습니다' }),
    unmappingSuccess: t({ en: 'Mapping removed', ko: '매핑이 해제되었습니다' }),

    // Tabs
    tabs: {
      overview: t({ en: 'Overview', ko: '개요' }),
      columns: t({ en: 'Columns', ko: '컬럼' }),
      tags: t({ en: 'Tags', ko: '태그' }),
      comments: t({ en: 'Comments', ko: '댓글' }),
    },
  },
} satisfies Dictionary

export default catalogContent
