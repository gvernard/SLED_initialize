import astropy.units as u
import astropy.wcs as pywcs
import numpy as np

from astropy.io import fits


def image_angle_from_cd(cd, unit=u.deg):
    """Return the rotation angle of the image.

    Defined such that a rotation angle of zero aligns north along the positive
    Y axis, and a positive rotation angle rotates north away from the Y axis,
    in the sense of a rotation from north to east.

    Note that the rotation angle is defined in a flat map-projection of the
    sky. It is what would be seen if the pixels of the image were drawn with
    their pixel widths scaled by the angular pixel increments returned by the
    axis_increments_from_cd() method.

    If the CD matrix was derived from the archaic CROTA and CDELT FITS
    keywords, then the angle returned by this function is equal to CROTA.

    Parameters
    ----------
    cd : numpy.ndarray
        The 2x2 coordinate conversion matrix, with its elements
        ordered for multiplying a column vector in FITS (x,y) axis order.
    unit : `astropy.units.Unit`
        The unit to give the returned angle (degrees by default).

    Returns
    -------
    out : float
        The angle between celestial north and the Y axis of the image,
        in the sense of an eastward rotation of celestial north from
        the Y-axis. The angle is returned in the range -180 to 180
        degrees (or the equivalent for the specified unit).

    """

    # Get the angular increments of pixels along the Y and X axes
    step = axis_increments_from_cd(cd)

    # Get the determinant of the coordinate transformation matrix.
    cddet = np.linalg.det(cd)

    # The angle of a northward vector from the origin can be calculated by
    # first using the inverse of the CD matrix to calculate the equivalent
    # vector in pixel indexes, then calculating the angle of this vector to the
    # Y axis of the image array.
    north = np.arctan2(-cd[0, 1] * step[1] / cddet,
                       cd[0, 0] * step[0] / cddet)

    # Return the angle with the specified units.
    return (north * u.rad).to(unit).value



def axis_increments_from_cd(cd):
    """Return the angular increments of pixels along the Y and X axes
    of an image array whose coordinates are described by a specified
    FITS CD matrix.

    In MPDAF, images are a regular grid of square pixels on a flat
    projection of the celestial sphere. This function returns the
    angular width and height of these pixels on the sky, with signs
    that indicate whether the angle increases or decreases as one
    steps along the corresponding array axis. To keep plots
    consistent, regardless of the rotation angle of the image on the
    sky, the returned height is always positive, but the returned
    width is negative if a plot of the image with pixel 0,0 at the
    bottom left would place east anticlockwise of north, and positive
    otherwise.

    Parameters
    ----------
    cd : numpy.ndarray
        The 2x2 coordinate conversion matrix, with its elements
        ordered for multiplying a column vector in FITS (x,y) axis
        order.
    unit : `astropy.units.Unit`
        The angular units of the returned values.

    Returns
    -------
    out : numpy.ndarray
        (dy,dx). These are the angular increments of pixels along the
        Y and X axes of the image, returned with the same units as
        the contents of the CD matrix.

    """

    # The pixel dimensions are determined as follows. First note
    # that the coordinate transformation matrix looks as follows:
    #
    #    |r| = |M[0,0], M[0,1]| |col - get_crpix1()|
    #    |d|   |M[1,0], M[1,1]| |row - get_crpix2()|
    #
    # In this equation [col,row] are the indexes of a pixel in the
    # image array and [r,d] are the coordinates of this pixel on a
    # flat map-projection of the sky. If the celestial coordinates
    # of the observation are right ascension and declination, then d
    # is parallel to declination, and r is perpendicular to this,
    # pointing east. When the column index is incremented by 1, the
    # above equation indicates that r and d change by:
    #
    #    col_dr = M[0,0]   col_dd = M[1,0]
    #
    # The length of the vector from (0,0) to (col_dr,col_dd) is
    # the angular width of pixels along the X axis.
    #
    #    dx = sqrt(M[0,0]^2 + M[1,1]^2)
    #
    # Similarly, when the row index is incremented by 1, r and d
    # change by:
    #
    #    row_dr = M[0,1]   row_dd = M[1,1]
    #
    # The length of the vector from (0,0) to (row_dr,row_dd) is
    # the angular width of pixels along the Y axis.
    #
    #    dy = sqrt(M[0,1]^2 + M[1,1]^2)
    #
    # Calculate the width and height of the pixels as described above.

    dx = np.sqrt(cd[0, 0]**2 + cd[1, 0]**2)
    dy = np.sqrt(cd[0, 1]**2 + cd[1, 1]**2)

    # To decide what sign to give the step in X, we need to know
    # whether east is clockwise or anticlockwise of north when the
    # image is plotted with pixel 0,0 at the bottom left of the
    # plot. The angle of a northward vector from the origin can be
    # calculated by first using the inverse of the CD matrix to
    # calculate the equivalent vector in pixel indexes, then
    # calculating the angle of this vector to the Y axis of the
    # image array. Start by calculating the determinant of the CD
    # matrix.

    cddet = np.linalg.det(cd)

    # Calculate the rotation angle of a unit northward vector
    # clockwise of the Y axis.

    north = np.arctan2(-cd[0, 1] / cddet, cd[0, 0] / cddet)

    # Calculate the rotation angle of a unit eastward vector
    # clockwise of the Y axis.

    east = np.arctan2(cd[1, 1] / cddet, -cd[1, 0] / cddet)

    # Wrap the difference east-north into the range -pi to pi radians.

    from astropy.coordinates import Angle
    delta = Angle((east - north) * u.rad).wrap_at(np.pi * u.rad).value

    # If east is anticlockwise of north make the X-axis pixel increment
    # negative.

    if delta < 0.0:
        dx *= -1.0

    # Return the axis increments in python array-indexing order.

    return np.array([dy, dx])

