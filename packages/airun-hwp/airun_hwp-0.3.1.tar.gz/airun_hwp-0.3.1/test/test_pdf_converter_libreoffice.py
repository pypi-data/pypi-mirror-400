"""
LibreOffice PDF 변환기 테스트
"""
import os
import pytest
from pathlib import Path
from airun_hwp.writer.pdf_converter_libreoffice import (
    convert_hwpx_to_pdf,
    is_libreoffice_installed,
    PDFConverterLibreOffice
)


class TestLibreOfficeConverter:
    """LibreOffice 변환기 테스트"""

    def test_libreoffice_installed(self):
        """LibreOffice 설치 확인"""
        result = is_libreoffice_installed()
        assert isinstance(result, bool)
        # 결과가 True인 경우 LibreOffice가 설치된 것
        if result:
            print("✅ LibreOffice is installed")
        else:
            print("⚠️  LibreOffice is not installed")

    @pytest.mark.skipif(not is_libreoffice_installed(), reason="LibreOffice not installed")
    def test_convert_hwpx_to_pdf(self, tmp_path):
        """HWPX → PDF 변환 테스트"""
        # 실제 HWPX 파일이 없으므로 존재하지 않는 파일로 테스트
        output_path = str(tmp_path / "output.pdf")

        result = convert_hwpx_to_pdf("/nonexistent/file.hwpx", output_path)

        # 존재하지 않는 파일이므로 None 반환
        assert result is None

    @pytest.mark.skipif(not is_libreoffice_installed(), reason="LibreOffice not installed")
    def test_converter_class(self, tmp_path):
        """PDFConverterLibreOffice 클래스 테스트"""
        converter = PDFConverterLibreOffice(timeout=30)
        assert converter.timeout == 30

        # 존재하지 않는 파일로 테스트
        output_path = str(tmp_path / "output.pdf")
        result = converter.convert("/nonexistent/file.hwpx", output_path)

        # 실패해야 함
        assert result is False

    def test_nonexistent_file(self):
        """존재하지 않는 파일 테스트"""
        result = convert_hwpx_to_pdf("/nonexistent/file.hwpx")
        assert result is None

    def test_converter_timeout_default(self):
        """기본 타임아웃 값 테스트"""
        converter = PDFConverterLibreOffice()
        assert converter.timeout == 30

    def test_converter_custom_timeout(self):
        """사용자 정의 타임아웃 값 테스트"""
        converter = PDFConverterLibreOffice(timeout=60)
        assert converter.timeout == 60
