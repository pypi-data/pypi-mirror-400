"""
LibreOffice headless 모드를 사용한 HWP/HWPX → PDF 변환기

이 모듈은 LibreOffice의 HWP/HWPX 필터를 사용하여
원문 형식을 보존하며 PDF로 변환합니다.
"""
import os
import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def is_libreoffice_installed() -> bool:
    """
    LibreOffice가 설치되어 있는지 확인

    Returns:
        bool: 설치되어 있으면 True, 아니면 False
    """
    try:
        result = subprocess.run(
            ['libreoffice', '--version'],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def convert_hwpx_to_pdf(
    hwpx_path: str,
    output_path: Optional[str] = None,
    timeout: int = 30
) -> Optional[str]:
    """
    HWP/HWPX 파일을 PDF로 변환

    Args:
        hwpx_path: HWP/HWPX 파일 경로
        output_path: 출력 PDF 파일 경로 (None인 경우 입력 파일과 같은 디렉토리)
        timeout: 변환 타임아웃 (초)

    Returns:
        변환된 PDF 파일 경로 (성공 시) 또는 None (실패 시)
    """
    try:
        if not os.path.exists(hwpx_path):
            logger.error(f"HWP/HWPX 파일 없음: {hwpx_path}")
            return None

        # LibreOffice 설치 확인
        if not is_libreoffice_installed():
            logger.error("LibreOffice가 설치되지 않음")
            return None

        # 출력 경로 결정
        if output_path is None:
            output_dir = os.path.dirname(hwpx_path)
            pdf_filename = Path(hwpx_path).stem + '.pdf'
            output_path = os.path.join(output_dir, pdf_filename)
        else:
            output_dir = os.path.dirname(output_path)

        # 원본 작업 디렉토리 저장
        original_cwd = os.getcwd()

        try:
            # 작업 디렉토리를 출력 디렉토리로 변경
            logger.info(f"변환 시작: {hwpx_path}")
            os.chdir(output_dir)

            # LibreOffice로 변환
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                os.path.basename(hwpx_path)
            ]

            logger.debug(f"실행 명령: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # LibreOffice는 에러를 출력하더라도 PDF를 생성할 수 있음
            # stderr에 "Unspecified Application Error"가 있어도 무시하고 PDF 확인

            # 변환된 PDF 파일 확인 (returncode와 상관없이)
            expected_pdf = os.path.join(output_dir, Path(hwpx_path).stem + '.pdf')

            # PDF 파일이 생성되었는지 확인
            if os.path.exists(expected_pdf):
                # PDF 생성 성공!
                if result.returncode != 0:
                    logger.warning(f"LibreOffice returned error code but PDF was created")
                    if result.stderr:
                        logger.debug(f"LibreOffice stderr: {result.stderr[:200]}")  # 첫 200자만 로그
                return output_path
            else:
                # PDF 파일이 생성되지 않음
                logger.error(f"PDF 파일 생성 실패: {expected_pdf}")
                if result.returncode != 0:
                    logger.error(f"LibreOffice 변환 실패 (returncode={result.returncode})")
                    if result.stderr:
                        logger.error(f"LibreOffice stderr: {result.stderr}")
                return None

            # 지정된 출력 경로로 이동 (필요한 경우)
            if expected_pdf != output_path:
                os.rename(expected_pdf, output_path)

            logger.info(f"PDF 변환 성공: {output_path}")
            return output_path

        except subprocess.TimeoutExpired:
            logger.error(f"변환 타임아웃 ({timeout}초 초과)")
            return None
        finally:
            # 원래 작업 디렉토리 복원
            os.chdir(original_cwd)

    except Exception as e:
        logger.error(f"PDF 변환 오류: {e}", exc_info=True)
        return None


class PDFConverterLibreOffice:
    """
    LibreOffice를 사용한 PDF 변환기 클래스

    기존 PDFConverter와 호환되는 인터페이스 제공
    """

    def __init__(self, timeout: int = 30):
        """
        Args:
            timeout: 변환 타임아웃 (초), 기본값 30초
        """
        self.timeout = timeout

    def convert(self, hwpx_path: str, pdf_path: str) -> bool:
        """
        HWP/HWPX 파일을 PDF로 변환

        Args:
            hwpx_path: HWP/HWPX 파일 경로
            pdf_path: 출력 PDF 파일 경로

        Returns:
            성공 시 True, 실패 시 False
        """
        result = convert_hwpx_to_pdf(hwpx_path, pdf_path, self.timeout)
        return result is not None
