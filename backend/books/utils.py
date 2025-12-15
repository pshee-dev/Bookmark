
# str->int 변환을 안전하게 처리하는 함수. (필요시 전역 유틸함수로 변경 가능)
def str_to_int(value, default, min_v=None, max_v=None):
    try:
        n = int(value)  
    except (TypeError, ValueError): # value가 없거나 숫자 형태가 아닌 경우
        n = default # 실패하면 default로 대체한다 
    
    # 숫자 크기 제한이 필요할 경우 
    if min_v is not None:
        n = max(min_v, n)  # n이 min_v보다 작으면 min_v로 끌어올림
    if max_v is not None:
        n = min(max_v, n)  # n이 max_v보다 크면 max_v로 끌어내림

    return n  # 최종 숫자 반환