
FORTRAN_CODE_MODULE_TEMPLATE = """
module {{MODULE_NAME}}  
implicit none 

{{PARAMETERS}} 

contains

{{FUNCTIONS}} 

end module {{MODULE_NAME}} 
"""

FORTRAN_CODE_MASK_FN_TEMPLATE = """
subroutine mask(is_in_lattice, x, y, z)
real*8, intent(in)   :: x, y, z
integer, intent(out)  :: is_in_lattice ! 0 = when outside and > 0 when inside the lattice 

! -----------------------------------
! YOUR CODE HERE
! -----------------------------------
is_in_lattice = 1


end subroutine
"""