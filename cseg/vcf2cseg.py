from .cpp.vcf2cseg_cpp import convert_vcf_to_cseg

def vcf_to_cseg(vcf_file_path, cseg_file_path):
    """Convert VCF file to CSEG format
    
    Args:
        vcf_file_path (str): Path to input VCF file
        cseg_file_path (str): Path to output CSEG file
    """
    with open(vcf_file_path, 'r') as vcf_file:
        vcf_content = vcf_file.read()
    
    cseg_content = convert_vcf_to_cseg(vcf_content)
    
    with open(cseg_file_path, 'w') as cseg_file:
        cseg_file.write(cseg_content)
