import streamlit as st
import pickle
import numpy as np
from bundle_reccommendation import bundle_reccommendation, upsale

def load_model():
    try:
        return pickle.load(open('toy_bundle_recommenders.pkl','rb'), encoding='utf-8')
    except Exception as e:
        st.error(f'Lỗi khi tải model: {str(e)}')
        return None

def main():
    st.title('🏨 Hệ thống Gợi ý Gói Dịch vụ Khách sạn')

    # Initialize session states
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'selected_bundles' not in st.session_state:
        st.session_state.selected_bundles = set()  
    if 'show_upsale' not in st.session_state:
        st.session_state.show_upsale = False
        
    # Sidebar cho input
    with st.sidebar:
        st.header('Thông tin đặt phòng')
        
        num_adults = st.number_input('Số người lớn:', 
                                   min_value=1, 
                                   max_value=10,
                                   value=2)
        
        num_children = st.number_input('Số trẻ em:',
                                   min_value=0,
                                   max_value=5,
                                   value=0)
        
        num_infants = st.number_input('Số trẻ sơ sinh:',
                                   min_value=0,
                                   max_value=3, 
                                   value=0)
        
        arrival_month = st.selectbox('Tháng đến:',
                               range(1,13))
        
        num_nights = st.number_input('Số đêm:',
                                 min_value=1,
                                 max_value=30,
                                 value=2)
        
        weekend = st.checkbox('Cuối tuần', value=False)
        holiday = st.checkbox('Ngày lễ', value=False)
        
        customer_origin = st.selectbox('Vùng miền:',
                                    ['North', 'South', 'Middle', 'Oversea'])
        
        hotel_name = st.selectbox('Khách sạn:', [
            'VinHolidays Fiesta Phú Quốc',
            'Vinpearl Luxury Nha Trang',
            'Vinpearl Beachfront Nha Trang',
            'Vinpearl Wonderworld Phú Quốc',
            'Vinpearl Resort & Spa Hạ Long',
            'Vinpearl Resort Nha Trang',
            'Vinpearl Resort & Spa Nha Trang Bay',
            'Vinpearl Resort & Golf Nam Hội An',
            'Vinpearl Resort & Spa Phú Quốc',
            'Hòn Tằm Resort'
        ])

    # Main content
    search_button = st.button('Tìm gói dịch vụ phù hợp')
    
    if search_button:
        bundle_recommender = load_model()
        if bundle_recommender is not None:
            try:
                st.session_state.recommendations = bundle_reccommendation(
                    hotel_name=hotel_name,
                    num_of_adults=num_adults,
                    num_of_childrens=num_children,
                    num_of_infants=num_infants,
                    arrival_month=arrival_month,
                    num_nights=num_nights,
                    weekend=weekend,
                    holiday=holiday,
                    customer_origin=customer_origin
                )
                # Reset các state khác khi tìm kiếm mới
                st.session_state.selected_bundles = set()
                st.session_state.show_upsale = False
            except Exception as e:
                st.error(f'Lỗi khi tìm kiếm gói: {str(e)}')

    # Hiển thị kết quả nếu có recommendations
    if st.session_state.recommendations is not None:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header('Các gói dịch vụ đề xuất')
            recommendations = sorted(st.session_state.recommendations, 
                                  key=lambda x: x['prob'], 
                                  reverse=True)
            
            # Hiển thị top 10 gói có xác suất cao nhất
            for i, rec in enumerate(recommendations[:10]):
                bundle_items = tuple(sorted(rec['bundle']))
                with st.expander(f"Gói {i+1} (Độ phù hợp: {rec['prob']:.2%})"):
                    for item in rec['bundle']:
                        st.write(f"- {item}")
                    # Checkbox để chọn gói
                    if st.checkbox('Chọn gói này', 
                                 key=f'select_{i}',
                                 value=bundle_items in st.session_state.selected_bundles):
                        st.session_state.selected_bundles.add(bundle_items)
                    else:
                        if bundle_items in st.session_state.selected_bundles:
                            st.session_state.selected_bundles.remove(bundle_items)

        with col2:
            st.header('Gói đã chọn')
            if st.session_state.selected_bundles:
                for i, bundle in enumerate(st.session_state.selected_bundles):
                    with st.expander(f"Gói đã chọn {i+1}"):
                        for item in bundle:
                            st.write(f"- {item}")
                
                confirm_col, clear_col = st.columns(2)
                with confirm_col:
                    if st.button('Xác nhận', type='primary'):
                        st.session_state.show_upsale = True
                
                with clear_col:
                    if st.button('Xóa tất cả'):
                        st.session_state.selected_bundles = set()
                        st.session_state.show_upsale = False
                        st.rerun()
            else:
                st.info('Chưa có gói nào được chọn')

        # Hiển thị đề xuất bổ sung sau khi xác nhận
        if st.session_state.show_upsale:
            st.header('Đề xuất bổ sung')
            
            selected_items = []
            for bundle in st.session_state.selected_bundles:
                selected_items.extend(list(bundle))
            
            try:
                upsale_recommendations = upsale(
                    hotel_name=hotel_name,
                    num_of_adults=num_adults,
                    num_of_childrens=num_children,
                    num_of_infants=num_infants,
                    arrival_month=arrival_month,
                    num_nights=num_nights,
                    weekend=weekend,
                    holiday=holiday,
                    customer_origin=customer_origin,
                    bought_items=selected_items
                )
                
                upsale_recommendations = sorted(upsale_recommendations, 
                                             key=lambda x: x['score'], 
                                             reverse=True)
                
                for i, rec in enumerate(upsale_recommendations[:5]):
                    with st.expander(f"Gói bổ sung {i+1} (Điểm phù hợp: {rec['score']:.2f})"):
                        st.write("**Các dịch vụ bổ sung:**")
                        new_items = set(rec['bundle']) - set(selected_items)
                        if new_items:
                            for item in new_items:
                                st.write(f"- {item}")
                        else:
                            st.info("Gói này đã bao gồm trong lựa chọn của bạn")
            except Exception as e:
                st.error(f'Lỗi khi tạo đề xuất bổ sung: {str(e)}')
    else:
        st.info('Vui lòng nhập thông tin và nhấn "Tìm gói dịch vụ phù hợp"')

if __name__ == '__main__':
    main()