import { useState, useEffect, useCallback, useRef } from 'react'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

interface UseApiResult<T> extends UseApiState<T> {
  refetch: () => Promise<void>
  mutate: (data: T) => void
}

/**
 * Custom hook for API data fetching with loading and error states
 */
export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = []
): UseApiResult<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  })

  // Use ref to store latest fetcher to avoid infinite loops
  const fetcherRef = useRef(fetcher)
  fetcherRef.current = fetcher

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }))
    try {
      const data = await fetcherRef.current()
      setState({ data, loading: false, error: null })
    } catch (error) {
      setState({ data: null, loading: false, error: error as Error })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const mutate = useCallback((data: T) => {
    setState((prev) => ({ ...prev, data }))
  }, [])

  return {
    ...state,
    refetch: fetchData,
    mutate,
  }
}

interface UseMutationState<T> {
  data: T | null
  loading: boolean
  error: Error | null
}

interface UseMutationResult<TData, TVariables> extends UseMutationState<TData> {
  mutate: (variables: TVariables) => Promise<TData>
  reset: () => void
}

/**
 * Custom hook for API mutations (POST, PUT, DELETE)
 */
export function useMutation<TData, TVariables>(
  mutator: (variables: TVariables) => Promise<TData>
): UseMutationResult<TData, TVariables> {
  const [state, setState] = useState<UseMutationState<TData>>({
    data: null,
    loading: false,
    error: null,
  })

  const mutate = useCallback(
    async (variables: TVariables): Promise<TData> => {
      setState({ data: null, loading: true, error: null })
      try {
        const data = await mutator(variables)
        setState({ data, loading: false, error: null })
        return data
      } catch (error) {
        setState({ data: null, loading: false, error: error as Error })
        throw error
      }
    },
    [mutator]
  )

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null })
  }, [])

  return {
    ...state,
    mutate,
    reset,
  }
}
