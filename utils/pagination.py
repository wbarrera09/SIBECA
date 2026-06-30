import streamlit as st

from utils.ui import GOES_BLUE


def apply_pagination_styles():
    st.markdown(
        f"""
        <style>
            div[class*="sibeca_pager_controls"] {{
                margin-top: 4px !important;
                margin-bottom: 10px !important;
            }}

            div[class*="sibeca_pager_prev"] button,
            div[class*="sibeca_pager_next"] button {{
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: {GOES_BLUE} !important;
                min-height: 34px !important;
                height: 34px !important;
                width: 34px !important;
                min-width: 34px !important;
                max-width: 34px !important;
                padding: 0 !important;
                border-radius: 8px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                font-weight: 900 !important;
                margin: 0 !important;
            }}

            div[class*="sibeca_pager_prev"] button:hover,
            div[class*="sibeca_pager_next"] button:hover {{
                background: #f1f5f9 !important;
                color: {GOES_BLUE} !important;
                border: none !important;
                box-shadow: none !important;
            }}

            div[class*="sibeca_pager_prev"] button:disabled,
            div[class*="sibeca_pager_next"] button:disabled {{
                background: transparent !important;
                color: #cbd5e1 !important;
                opacity: 1 !important;
            }}

            div[class*="sibeca_pager_prev"] button p,
            div[class*="sibeca_pager_next"] button p,
            div[class*="sibeca_pager_prev"] button span,
            div[class*="sibeca_pager_next"] button span {{
                color: inherit !important;
                font-size: 1.35rem !important;
                font-weight: 900 !important;
                line-height: 1 !important;
                margin: 0 !important;
                padding: 0 !important;
            }}

            .sibeca-pager-label {{
                height: 34px;
                width: 74px;
                min-width: 74px;
                max-width: 74px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.9rem;
                font-weight: 800;
                color: {GOES_BLUE};
                white-space: nowrap;
                overflow: hidden;
                line-height: 1;
                text-align: center;
                box-sizing: border-box;
            }}

            .sibeca-pager-info {{
                height: 34px;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                font-size: 0.82rem;
                color: #64748b;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                line-height: 1;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )


def render_pagination(
    total_records,
    key_prefix,
    label="estudiantes",
    page_size_options=None,
    default_page_size=25
):
    apply_pagination_styles()

    if page_size_options is None:
        page_size_options = [10, 25, 50, 100]

    page_key = f"{key_prefix}_page_number"
    page_size_key = f"{key_prefix}_page_size"

    if page_key not in st.session_state:
        st.session_state[page_key] = 1

    with st.container(key=f"{key_prefix}_sibeca_pager_controls"):
        page_col_1, page_col_2, page_col_3, page_col_4, page_col_5 = st.columns(
            [1.25, 0.16, 0.42, 0.16, 4.8],
            vertical_alignment="bottom"
        )

        with page_col_1:
            page_size = st.selectbox(
                "Filas por página",
                options=page_size_options,
                index=page_size_options.index(default_page_size),
                key=page_size_key
            )

        total_pages = max((total_records - 1) // page_size + 1, 1)

        if st.session_state[page_key] > total_pages:
            st.session_state[page_key] = total_pages

        def previous_page():
            st.session_state[page_key] = max(
                1,
                st.session_state[page_key] - 1
            )

        def next_page():
            st.session_state[page_key] = min(
                total_pages,
                st.session_state[page_key] + 1
            )

        page_number = st.session_state[page_key]

        start_row = (page_number - 1) * page_size
        end_row = start_row + page_size

        display_start = start_row + 1 if total_records > 0 else 0
        display_end = min(end_row, total_records)

        with page_col_2:
            st.button(
                "‹",
                disabled=page_number <= 1,
                on_click=previous_page,
                key=f"{key_prefix}_sibeca_pager_prev"
            )

        with page_col_3:
            st.markdown(
                f"""
                <div class="sibeca-pager-label">
                    {page_number} / {total_pages}
                </div>
                """,
                unsafe_allow_html=True
            )

        with page_col_4:
            st.button(
                "›",
                disabled=page_number >= total_pages,
                on_click=next_page,
                key=f"{key_prefix}_sibeca_pager_next"
            )

        with page_col_5:
            st.markdown(
                f"""
                <div class="sibeca-pager-info">
                    Mostrando {display_start:,}–{display_end:,} de {total_records:,} {label}
                </div>
                """,
                unsafe_allow_html=True
            )

    return page_size, page_number, start_row, end_row