#define NP_NO_DEPRECATED_API NPY_1_7_API_VERSION
#define Py_LIMITED_API 0x030600f0

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
#include "dbg.h"
//#include <omp.h>

/* Define docstring */
static char module_docstring[] =
    "multivariate normal tools for C";
static char _gaussian_mixture_pdf_docstring[] =
    "Calculate the pdf of a Gaussian mixture.";
static char _gaussian_mixture_log_pdf_docstring[] =
    "Calculate the log pdf of a Gaussian mixture.";
static char _gm_pdf_global_limits_docstring[] =
    "Calculate the pdf of a Gaussian mixture with global limits.";
static char _gm_log_pdf_global_limits_docstring[] =
    "Calculate the log pdf of a Gaussian mixture with global limits.";
static char _gm_pdf_local_limits_docstring[] =
    "Calculate the pdf of a Gaussian mixture with component limits.";
static char _gm_log_pdf_local_limits_docstring[] =
    "Calculate the log pdf of a Gaussian mixture with component limits.";

/* Declare the C functions here */
static PyObject *_gaussian_mixture_pdf(PyObject *self, PyObject *args);
static PyObject *_gaussian_mixture_log_pdf(PyObject *self, PyObject *args);
static PyObject *_gm_pdf_global_limits(PyObject *self, PyObject *args);
static PyObject *_gm_log_pdf_global_limits(PyObject *self, PyObject *args);
static PyObject *_gm_pdf_local_limits(PyObject *self, PyObject *args);
static PyObject *_gm_log_pdf_local_limits(PyObject *self, PyObject *args);

/* Define the methods that will be available in the module */
static PyMethodDef module_methods[] = {
    {
    "_gaussian_mixture_pdf",
    _gaussian_mixture_pdf,
    METH_VARARGS,
    _gaussian_mixture_pdf_docstring,
   },
    {
    "_gaussian_mixture_log_pdf",
    _gaussian_mixture_log_pdf,
    METH_VARARGS,
    _gaussian_mixture_log_pdf_docstring,
   },
    {
    "_gm_pdf_global_limits",
    _gm_pdf_global_limits,
    METH_VARARGS,
    _gm_pdf_global_limits_docstring,
   },
    {
    "_gm_log_pdf_global_limits",
    _gm_log_pdf_global_limits,
    METH_VARARGS,
    _gm_log_pdf_global_limits_docstring,
   },
    {
    "_gm_pdf_local_limits",
    _gm_pdf_local_limits,
    METH_VARARGS,
    _gm_pdf_local_limits_docstring,
   },
    {
    "_gm_log_pdf_local_limits",
    _gm_log_pdf_local_limits,
    METH_VARARGS,
    _gm_log_pdf_local_limits_docstring,
   },
   {NULL, NULL, 0, NULL}
};

/* This is the function that will call on import */

#if PY_MAJOR_VERSION >= 3
    #define MOD_ERROR_VAL NULL
    #define MOD_SUCCESS_VAL(val) val
    #define MOD_INIT(name) PyMODINIT_FUNC PyInit_##name(void)
    #define MOD_DEF(ob, name, doc, methods) \
        static struct PyModuleDef moduledef = { \
          PyModuleDef_HEAD_INIT, name, doc, -1, methods, }; \
        ob = PyModule_Create(&moduledef);
#else
    #define MOD_ERROR_VAL
    #define MOD_SUCCESS_VAL(val)
    #define MOD_INIT(name) void init##name(void)
    #define MOD_DEF(ob, name, doc, methods) \
            ob = Py_InitModule3(name, methods, doc);
#endif

MOD_INIT(_gaussian_mixture_pdf)
{
    PyObject *m;
    MOD_DEF(m, "_gaussian_mixture_pdf", module_docstring, module_methods);
    if (m == NULL)
        return MOD_ERROR_VAL;
    import_array();
    return MOD_SUCCESS_VAL(m);
}

/* Define other functions here */
static PyObject *_gaussian_mixture_pdf(PyObject *self, PyObject *args) {

    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // npts will describe the number of sample points
    npy_intp npts = 0;
    // ndim
    npy_intp ndim = 0;
    // keep
    npy_intp keep = 0;
    // factor for constatns
    double const_factor = 0;
    // determinant
    double log_det_cov = 0;
    // minimum eigenvalue
    double eps = 0;
    // Initialize output dimensions
    npy_intp eig_dims[3];
    npy_intp out_dims[1];

    // Py_objects for inputs and output objects
    PyObject *mu_obj = NULL;
    PyObject *scale_obj = NULL;
    PyObject *weights_obj = NULL;
    PyObject *eigvals_obj = NULL;
    PyObject *eigvecs_obj = NULL;
    PyObject *sample_obj = NULL;
    PyObject *eigvecs_norm_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *mu_arr = NULL;
    PyArrayObject *scale_arr = NULL;
    PyArrayObject *weights_arr = NULL;
    PyArrayObject *eigvals_arr = NULL;
    PyArrayObject *eigvecs_arr = NULL;
    PyArrayObject *sample_arr = NULL;
    PyArrayObject *eigvecs_norm_arr = NULL;
    PyArrayObject *out_arr = NULL;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOOOOd", &mu_obj, &scale_obj, &weights_obj, &eigvals_obj, &eigvecs_obj, &sample_obj, &eps)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    // Check mu
    mu_arr = (PyArrayObject *)PyArray_FROM_O(mu_obj);
    check(mu_arr, "Failed to build mu_arr");
    check(PyArray_NDIM(mu_arr) == 2, "mu_arr should have 2 dimensions");

    // Check scale
    scale_arr = (PyArrayObject *)PyArray_FROM_O(scale_obj);
    check(scale_arr, "Failed to build scale_arr");
    check(PyArray_NDIM(scale_arr) == 2, "scale_arr should have 2 dimensions");

    // Check weights
    weights_arr = (PyArrayObject *)PyArray_FROM_O(weights_obj);
    check(weights_arr, "Failed to build weights_arr");
    check(PyArray_NDIM(weights_arr) == 1, "weights_arr should have 2 dimensions");

    // Check eigvals
    eigvals_arr = (PyArrayObject *)PyArray_FROM_O(eigvals_obj);
    check(eigvals_arr, "Failed to build eigvals_arr");
    check(PyArray_NDIM(eigvals_arr) == 2, "eigvals_arr should have 2 dimensions");

    // Check eigvecs
    eigvecs_arr = (PyArrayObject *)PyArray_FROM_O(eigvecs_obj);
    check(eigvecs_arr, "Failed to build eigvecs_arr");
    check(PyArray_NDIM(eigvecs_arr) == 3, "eigvecs_arr should have 2 dimensions");

    // Check sample
    sample_arr = (PyArrayObject *)PyArray_FROM_O(sample_obj);
    check(sample_arr, "Failed to build sample_arr");
    check(PyArray_NDIM(sample_arr) == 2, "sample_arr should have 2 dimensions");

    // Check dimensions
    ngauss = PyArray_DIM(mu_arr, 0);
    check(ngauss > 0, "ngauss should be greater than zero.");
    ndim = PyArray_DIM(mu_arr, 1);
    check(ndim > 0, "ndim should be greater than zero");
    npts = PyArray_DIM(sample_arr, 0);
    check(npts > 0, "npts should be greater than zero.");

    // Check scale
    check((PyArray_DIM(scale_arr, 0) == ngauss) & (PyArray_DIM(scale_arr, 1) == ndim),
        "Dimension mismatch between mu and scale.");
    // Check weights
    check((PyArray_DIM(weights_arr, 0) == ngauss),
        "Dimension mismatch between mu and weights.");
    // Check eigvals
    check((PyArray_DIM(eigvals_arr, 0) == ngauss) & (PyArray_DIM(eigvals_arr, 1) == ndim),
        "Dimension mismatch between mu and eigvals.");
    // Check eigvecs
    check(
          (PyArray_DIM(eigvecs_arr, 0) == ngauss) &
          (PyArray_DIM(eigvecs_arr, 1) == ndim) &
          (PyArray_DIM(eigvecs_arr, 2) == ndim),
          "Dimension mismatch between mu and eigvecs"
         );

    // Check sample
    check(PyArray_DIM(sample_arr, 1) == ndim,
        "Dimension mismatch between mu and sample.");


    // Build eigvecs_norm array
    // assign dims
    eig_dims[0] = ngauss;
    eig_dims[1] = ndim;
    eig_dims[2] = ndim;
    // make eigenvector norm object
    eigvecs_norm_obj = PyArray_ZEROS(3, eig_dims, NPY_DOUBLE, 0);
    check(eigvecs_norm_obj, "Failed to build eigvecs_norm_obj.");
    // Convert to array
    eigvecs_norm_arr = (PyArrayObject *) eigvecs_norm_obj;
    check(eigvecs_norm_arr, "Failed to build eigvecs_norm_arr.");
    // fill with zeroes
    PyArray_FILLWBYTE(eigvecs_norm_arr, 0);


    // Build output array
    // assign dims
    out_dims[0] = npts;
    // make out object
    out_obj = PyArray_ZEROS(1, out_dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    // Convert to array
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Assign constants
    const_factor = ((double)ndim) * log(2. * NPY_PI);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    // Loop through the gaussians
    for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){

        //// Calculate the log_det_cov ////

        // Initialize log_det_cov at 1
        log_det_cov = 1.;
        keep = 1;
        // Loop the dimensions
        for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
            // Find the eigenvalue pointer
            double *eigvals_ptr = PyArray_GETPTR2(eigvals_arr, gauss_id, dim1_id);
            // If the eigenvalue is greater than eps...
            if ((*eigvals_ptr) > eps) {
                // Then multiply its value into the determinant
                log_det_cov *= (*eigvals_ptr);
            // If not ... 
            } else {
                // singular matrix
                log_det_cov = 0;
                keep = 0;
            }
        }
        // Take the logarithm
        if (keep == 1) {
            log_det_cov = log(log_det_cov);
        }

        //// Calculate the orthonormalized eigenvectors ////
        // Only for non-singular eigenvalues:
        if (keep == 1) {
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                for (npy_intp dim2_id = 0; dim2_id < ndim; dim2_id++) {
                    // Find the eigenvalue pointer
                    double *eigvals_ptr = PyArray_GETPTR2(eigvals_arr, gauss_id, dim2_id);
                    // Find the eigenvector pointer
                    double *eigvecs_ptr = PyArray_GETPTR3(eigvecs_arr, gauss_id, dim1_id, dim2_id);
                    // Get the address of the vector
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim1_id, dim2_id);
                    // assign it a value
                    *eigvecs_norm_ptr =  (*eigvecs_ptr)/sqrt(*eigvals_ptr);
                }
            }
        }
    }
    // Close all threads; open new threads
    Py_END_ALLOW_THREADS
    Py_BEGIN_ALLOW_THREADS
    // Loop the output array
    #pragma omp parallel for
    for (npy_intp sample_id = 0; sample_id < npts; sample_id++){
        // find the out pointer
        double *out_ptr =              PyArray_GETPTR1(out_arr, sample_id);
        double out_buffer = 0;

        // Loop through the gaussians
        for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){
        
            // Identify weights
            double *weights_ptr =       PyArray_GETPTR1(weights_arr, gauss_id);
        
            //// First loop; Identify maximum component ////
            // reset the maha distance
            double maha = 0;
            // Loop k
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                // reset r
                double r = 0;
                // loop l
                for (npy_intp dim2_id =0; dim2_id < ndim; dim2_id++) {
                    double *mu_ptr = PyArray_GETPTR2(mu_arr, gauss_id, dim2_id);
                    double *scale_ptr = PyArray_GETPTR2(scale_arr, gauss_id, dim2_id);
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim2_id, dim1_id);
                    double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim2_id);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            // Identify log pdf for this Gaussian component
            out_buffer = (-0.5 * (const_factor + log_det_cov + maha)) 
                + (*weights_ptr);
            // Check if this is a new maximum
            if ((sample_id == 0) | (out_buffer > (*out_ptr))) {
                *out_ptr = out_buffer;
            }

        }
        // Identify maximum of logpdf for this Gaussian component
        out_buffer = *out_ptr;
        // Reset output array
        *out_ptr = 0;
        // Loop through the gaussians
        for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){
            // Identify weights
            double *weights_ptr =       PyArray_GETPTR1(weights_arr, gauss_id);
            //// Calculate the mahalanobis distance ////
            // reset the maha distance
            double maha = 0;
            // Loop k
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                // reset r
                double r = 0;
                // loop l
                for (npy_intp dim2_id =0; dim2_id < ndim; dim2_id++) {
                    double *mu_ptr = PyArray_GETPTR2(mu_arr, gauss_id, dim2_id);
                    double *scale_ptr = PyArray_GETPTR2(scale_arr, gauss_id, dim2_id);
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim2_id, dim1_id);
                    double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim2_id);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            // Add in shifted exponential space
            *out_ptr += exp(((-0.5 * (const_factor + log_det_cov + maha)) 
                + (*weights_ptr)) - out_buffer);
        }
        // Shift output back
        *out_ptr *= exp(out_buffer);
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS

    // Free things
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (weights_arr)        {Py_DECREF(weights_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    if (out_obj)            {Py_DECREF(out_obj);}
    if (out_arr)            {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_gaussian_mixture_log_pdf(PyObject *self, PyObject *args) {
    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // npts will describe the number of sample points
    npy_intp npts = 0;
    // ndim
    npy_intp ndim = 0;
    // keep
    npy_intp keep = 0;
    // factor for constatns
    double const_factor = 0;
    // determinant
    double log_det_cov = 0;
    // minimum eigenvalue
    double eps = 0;
    // Initialize output dimensions
    npy_intp eig_dims[3];
    npy_intp out_dims[1];

    // Py_objects for inputs and output objects
    PyObject *mu_obj = NULL;
    PyObject *scale_obj = NULL;
    PyObject *weights_obj = NULL;
    PyObject *eigvals_obj = NULL;
    PyObject *eigvecs_obj = NULL;
    PyObject *sample_obj = NULL;
    PyObject *eigvecs_norm_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *mu_arr = NULL;
    PyArrayObject *scale_arr = NULL;
    PyArrayObject *weights_arr = NULL;
    PyArrayObject *eigvals_arr = NULL;
    PyArrayObject *eigvecs_arr = NULL;
    PyArrayObject *sample_arr = NULL;
    PyArrayObject *eigvecs_norm_arr = NULL;
    PyArrayObject *out_arr = NULL;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOOOOd", &mu_obj, &scale_obj, &weights_obj, &eigvals_obj, &eigvecs_obj, &sample_obj, &eps)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    // Check mu
    mu_arr = (PyArrayObject *)PyArray_FROM_O(mu_obj);
    check(mu_arr, "Failed to build mu_arr");
    check(PyArray_NDIM(mu_arr) == 2, "mu_arr should have 2 dimensions");

    // Check scale
    scale_arr = (PyArrayObject *)PyArray_FROM_O(scale_obj);
    check(scale_arr, "Failed to build scale_arr");
    check(PyArray_NDIM(scale_arr) == 2, "scale_arr should have 2 dimensions");

    // Check weights
    weights_arr = (PyArrayObject *)PyArray_FROM_O(weights_obj);
    check(weights_arr, "Failed to build weights_arr");
    check(PyArray_NDIM(weights_arr) == 1, "weights_arr should have 2 dimensions");

    // Check eigvals
    eigvals_arr = (PyArrayObject *)PyArray_FROM_O(eigvals_obj);
    check(eigvals_arr, "Failed to build eigvals_arr");
    check(PyArray_NDIM(eigvals_arr) == 2, "eigvals_arr should have 2 dimensions");

    // Check eigvecs
    eigvecs_arr = (PyArrayObject *)PyArray_FROM_O(eigvecs_obj);
    check(eigvecs_arr, "Failed to build eigvecs_arr");
    check(PyArray_NDIM(eigvecs_arr) == 3, "eigvecs_arr should have 2 dimensions");

    // Check sample
    sample_arr = (PyArrayObject *)PyArray_FROM_O(sample_obj);
    check(sample_arr, "Failed to build sample_arr");
    check(PyArray_NDIM(sample_arr) == 2, "sample_arr should have 2 dimensions");

    // Check dimensions
    ngauss = PyArray_DIM(mu_arr, 0);
    check(ngauss > 0, "ngauss should be greater than zero.");
    ndim = PyArray_DIM(mu_arr, 1);
    check(ndim > 0, "ndim should be greater than zero");
    npts = PyArray_DIM(sample_arr, 0);
    check(npts > 0, "npts should be greater than zero.");

    // Check scale
    check((PyArray_DIM(scale_arr, 0) == ngauss) & (PyArray_DIM(scale_arr, 1) == ndim),
        "Dimension mismatch between mu and scale.");
    // Check weights
    check((PyArray_DIM(weights_arr, 0) == ngauss),
        "Dimension mismatch between mu and weights.");
    // Check eigvals
    check((PyArray_DIM(eigvals_arr, 0) == ngauss) & (PyArray_DIM(eigvals_arr, 1) == ndim),
        "Dimension mismatch between mu and eigvals.");
    // Check eigvecs
    check(
          (PyArray_DIM(eigvecs_arr, 0) == ngauss) &
          (PyArray_DIM(eigvecs_arr, 1) == ndim) &
          (PyArray_DIM(eigvecs_arr, 2) == ndim),
          "Dimension mismatch between mu and eigvecs"
         );

    // Check sample
    check(PyArray_DIM(sample_arr, 1) == ndim,
        "Dimension mismatch between mu and sample.");


    // Build eigvecs_norm array
    // assign dims
    eig_dims[0] = ngauss;
    eig_dims[1] = ndim;
    eig_dims[2] = ndim;
    // make eigenvector norm object
    eigvecs_norm_obj = PyArray_ZEROS(3, eig_dims, NPY_DOUBLE, 0);
    check(eigvecs_norm_obj, "Failed to build eigvecs_norm_obj.");
    // Convert to array
    eigvecs_norm_arr = (PyArrayObject *) eigvecs_norm_obj;
    check(eigvecs_norm_arr, "Failed to build eigvecs_norm_arr.");
    // fill with zeroes
    PyArray_FILLWBYTE(eigvecs_norm_arr, 0);


    // Build output array
    // assign dims
    out_dims[0] = npts;
    // make out object
    out_obj = PyArray_ZEROS(1, out_dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    // Convert to array
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Assign constants
    const_factor = ((double)ndim) * log(2. * NPY_PI);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    // Loop through the gaussians
    for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){

        //// Calculate the log_det_cov ////

        // Initialize log_det_cov at 1
        log_det_cov = 1.;
        keep = 1;
        // Loop the dimensions
        for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
            // Find the eigenvalue pointer
            double *eigvals_ptr = PyArray_GETPTR2(eigvals_arr, gauss_id, dim1_id);
            // If the eigenvalue is greater than eps...
            if ((*eigvals_ptr) > eps) {
                // Then multiply its value into the determinant
                log_det_cov *= (*eigvals_ptr);
            // If not ... 
            } else {
                // singular matrix
                log_det_cov = 0;
                keep = 0;
            }
        }
        // Take the logarithm
        if (keep == 1) {
            log_det_cov = log(log_det_cov);
        }

        //// Calculate the orthonormalized eigenvectors ////
        // Only for non-singular eigenvalues:
        if (keep == 1) {
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                for (npy_intp dim2_id = 0; dim2_id < ndim; dim2_id++) {
                    // Find the eigenvalue pointer
                    double *eigvals_ptr = PyArray_GETPTR2(eigvals_arr, gauss_id, dim2_id);
                    // Find the eigenvector pointer
                    double *eigvecs_ptr = PyArray_GETPTR3(eigvecs_arr, gauss_id, dim1_id, dim2_id);
                    // Get the address of the vector
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim1_id, dim2_id);
                    // assign it a value
                    *eigvecs_norm_ptr =  (*eigvecs_ptr)/sqrt(*eigvals_ptr);
                }
            }
        }
    }
    // Close all threads; open new threads
    Py_END_ALLOW_THREADS
    Py_BEGIN_ALLOW_THREADS
    // Loop the output array
    #pragma omp parallel for
    for (npy_intp sample_id = 0; sample_id < npts; sample_id++){
        // find the out pointer
        double *out_ptr =              PyArray_GETPTR1(out_arr, sample_id);
        double out_buffer = 0;

        // Loop through the gaussians
        for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){
        
            // Identify weights
            double *weights_ptr =       PyArray_GETPTR1(weights_arr, gauss_id);
        
            //// First loop; Identify maximum component ////
            // reset the maha distance
            double maha = 0;
            // Loop k
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                // reset r
                double r = 0;
                // loop l
                for (npy_intp dim2_id =0; dim2_id < ndim; dim2_id++) {
                    double *mu_ptr = PyArray_GETPTR2(mu_arr, gauss_id, dim2_id);
                    double *scale_ptr = PyArray_GETPTR2(scale_arr, gauss_id, dim2_id);
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim2_id, dim1_id);
                    double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim2_id);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            // Identify log pdf for this Gaussian component
            out_buffer = (-0.5 * (const_factor + log_det_cov + maha)) 
                + (*weights_ptr);
            // Check if this is a new maximum
            if ((sample_id == 0) | (out_buffer > (*out_ptr))) {
                *out_ptr = out_buffer;
            }

        }
        // Identify maximum of logpdf for this Gaussian component
        out_buffer = *out_ptr;
        // Reset output array
        *out_ptr = 0;
        // Loop through the gaussians
        for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){
            // Identify weights
            double *weights_ptr =       PyArray_GETPTR1(weights_arr, gauss_id);
            //// Calculate the mahalanobis distance ////
            // reset the maha distance
            double maha = 0;
            // Loop k
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                // reset r
                double r = 0;
                // loop l
                for (npy_intp dim2_id =0; dim2_id < ndim; dim2_id++) {
                    double *mu_ptr = PyArray_GETPTR2(mu_arr, gauss_id, dim2_id);
                    double *scale_ptr = PyArray_GETPTR2(scale_arr, gauss_id, dim2_id);
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim2_id, dim1_id);
                    double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim2_id);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            // Add in shifted exponential space
            *out_ptr += exp(((-0.5 * (const_factor + log_det_cov + maha)) 
                + (*weights_ptr)) - out_buffer);
        }
        // Shift output back
        *out_ptr = log(*out_ptr) + out_buffer;
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS

    // Free things
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (weights_arr)        {Py_DECREF(weights_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (weights_arr)        {Py_DECREF(weights_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    if (out_obj)            {Py_DECREF(out_obj);}
    if (out_arr)            {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

/* Define other functions here */
static PyObject *_gm_pdf_global_limits(PyObject *self, PyObject *args) {
    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // npts will describe the number of sample points
    npy_intp npts = 0;
    // ndim
    npy_intp ndim = 0;
    // keep
    npy_intp keep = 0;
    // factor for constatns
    double const_factor = 0;
    // determinant
    double log_det_cov = 0;
    // minimum eigenvalue
    double eps = 0;
    // Initialize output dimensions
    npy_intp eig_dims[3];
    npy_intp out_dims[1];

    // Py_objects for inputs and output objects
    PyObject *mu_obj = NULL;
    PyObject *scale_obj = NULL;
    PyObject *weights_obj = NULL;
    PyObject *eigvals_obj = NULL;
    PyObject *eigvecs_obj = NULL;
    PyObject *limits_obj = NULL;
    PyObject *sample_obj = NULL;
    PyObject *eigvecs_norm_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *mu_arr = NULL;
    PyArrayObject *scale_arr = NULL;
    PyArrayObject *weights_arr = NULL;
    PyArrayObject *eigvals_arr = NULL;
    PyArrayObject *eigvecs_arr = NULL;
    PyArrayObject *limits_arr = NULL;
    PyArrayObject *sample_arr = NULL;
    PyArrayObject *eigvecs_norm_arr = NULL;
    PyArrayObject *out_arr = NULL;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOOOOOd", &mu_obj, &scale_obj, &weights_obj, &eigvals_obj, &eigvecs_obj, &limits_obj, &sample_obj, &eps)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    // Check mu
    mu_arr = (PyArrayObject *)PyArray_FROM_O(mu_obj);
    check(mu_arr, "Failed to build mu_arr");
    check(PyArray_NDIM(mu_arr) == 2, "mu_arr should have 2 dimensions");

    // Check scale
    scale_arr = (PyArrayObject *)PyArray_FROM_O(scale_obj);
    check(scale_arr, "Failed to build scale_arr");
    check(PyArray_NDIM(scale_arr) == 2, "scale_arr should have 2 dimensions");

    // Check weights
    weights_arr = (PyArrayObject *)PyArray_FROM_O(weights_obj);
    check(weights_arr, "Failed to build weights_arr");
    check(PyArray_NDIM(weights_arr) == 1, "weights_arr should have 2 dimensions");

    // Check eigvals
    eigvals_arr = (PyArrayObject *)PyArray_FROM_O(eigvals_obj);
    check(eigvals_arr, "Failed to build eigvals_arr");
    check(PyArray_NDIM(eigvals_arr) == 2, "eigvals_arr should have 2 dimensions");

    // Check eigvecs
    eigvecs_arr = (PyArrayObject *)PyArray_FROM_O(eigvecs_obj);
    check(eigvecs_arr, "Failed to build eigvecs_arr");
    check(PyArray_NDIM(eigvecs_arr) == 3, "eigvecs_arr should have 2 dimensions");

    // Check limits
    limits_arr = (PyArrayObject *)PyArray_FROM_O(limits_obj);
    check(limits_arr, "Failed to build limits_arr");
    check(PyArray_NDIM(limits_arr) == 2, "limits_arr should have 2 dimensions");

    // Check sample
    sample_arr = (PyArrayObject *)PyArray_FROM_O(sample_obj);
    check(sample_arr, "Failed to build sample_arr");
    check(PyArray_NDIM(sample_arr) == 2, "sample_arr should have 2 dimensions");

    // Check dimensions
    ngauss = PyArray_DIM(mu_arr, 0);
    check(ngauss > 0, "ngauss should be greater than zero.");
    ndim = PyArray_DIM(mu_arr, 1);
    check(ndim > 0, "ndim should be greater than zero");
    npts = PyArray_DIM(sample_arr, 0);
    check(npts > 0, "npts should be greater than zero.");

    // Check scale
    check((PyArray_DIM(scale_arr, 0) == ngauss) & (PyArray_DIM(scale_arr, 1) == ndim),
        "Dimension mismatch between mu and scale.");
    // Check weights
    check((PyArray_DIM(weights_arr, 0) == ngauss),
        "Dimension mismatch between mu and weights.");
    // Check eigvals
    check((PyArray_DIM(eigvals_arr, 0) == ngauss) & (PyArray_DIM(eigvals_arr, 1) == ndim),
        "Dimension mismatch between mu and eigvals.");
    // Check eigvecs
    check(
          (PyArray_DIM(eigvecs_arr, 0) == ngauss) &
          (PyArray_DIM(eigvecs_arr, 1) == ndim) &
          (PyArray_DIM(eigvecs_arr, 2) == ndim),
          "Dimension mismatch between mu and eigvecs"
         );

    // Check limits
    check(
          (PyArray_DIM(limits_arr, 0) == ndim) &
          (PyArray_DIM(limits_arr, 1) == 2),
          "Dimension mismatch between mu and limits"
         );

    // Check sample
    check(PyArray_DIM(sample_arr, 1) == ndim,
        "Dimension mismatch between mu and sample.");


    // Build eigvecs_norm array
    // assign dims
    eig_dims[0] = ngauss;
    eig_dims[1] = ndim;
    eig_dims[2] = ndim;
    // make eigenvector norm object
    eigvecs_norm_obj = PyArray_ZEROS(3, eig_dims, NPY_DOUBLE, 0);
    check(eigvecs_norm_obj, "Failed to build eigvecs_norm_obj.");
    // Convert to array
    eigvecs_norm_arr = (PyArrayObject *) eigvecs_norm_obj;
    check(eigvecs_norm_arr, "Failed to build eigvecs_norm_arr.");
    // fill with zeroes
    PyArray_FILLWBYTE(eigvecs_norm_arr, 0);


    // Build output array
    // assign dims
    out_dims[0] = npts;
    // make out object
    out_obj = PyArray_ZEROS(1, out_dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    // Convert to array
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Assign constants
    const_factor = ((double)ndim) * log(2. * NPY_PI);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    // Loop through the gaussians
    for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){

        //// Calculate the log_det_cov ////
        // Initialize log_det_cov at 1
        log_det_cov = 1.;
        keep = 1;
        // Loop the dimensions
        for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
            // Find the eigenvalue pointer
            double *eigvals_ptr = PyArray_GETPTR2(eigvals_arr, gauss_id, dim1_id);
            // If the eigenvalue is greater than eps...
            if ((*eigvals_ptr) > eps) {
                // Then multiply its value into the determinant
                log_det_cov *= (*eigvals_ptr);
            // If not ... 
            } else {
                // singular matrix
                log_det_cov = 0;
                keep = 0;
            }
        }
        // Take the logarithm
        if (keep == 1) {
            log_det_cov = log(log_det_cov);
        }

        //// Calculate the orthonormalized eigenvectors ////
        // Only for non-singular eigenvalues:
        if (keep == 1) {
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                for (npy_intp dim2_id = 0; dim2_id < ndim; dim2_id++) {
                    // Find the eigenvalue pointer
                    double *eigvals_ptr = PyArray_GETPTR2(eigvals_arr, gauss_id, dim2_id);
                    // Find the eigenvector pointer
                    double *eigvecs_ptr = PyArray_GETPTR3(eigvecs_arr, gauss_id, dim1_id, dim2_id);
                    // Get the address of the vector
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim1_id, dim2_id);
                    // assign it a value
                    *eigvecs_norm_ptr =  (*eigvecs_ptr)/sqrt(*eigvals_ptr);
                }
            }
        }
    }
    // Close all threads; open new threads
    Py_END_ALLOW_THREADS
    Py_BEGIN_ALLOW_THREADS
    // Loop the output array
    #pragma omp parallel for
    for (npy_intp sample_id = 0; sample_id < npts; sample_id++){
        // find the out pointer
        double *out_ptr =              PyArray_GETPTR1(out_arr, sample_id);
        double out_buffer = 0;
        // Check global limits //
        npy_intp skip = 0;
        for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++){
            double *limits_lo_ptr = PyArray_GETPTR2(limits_arr, dim1_id, 0);
            double *limits_hi_ptr = PyArray_GETPTR2(limits_arr, dim1_id, 1);
            double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim1_id);
            if (
                (*sample_ptr < *limits_lo_ptr) | (*sample_ptr > *limits_hi_ptr)
            ) {
            skip += 1;
            }
        }
        // skip if not in limits //
        if (skip > 0) {
            continue;
        }
        // Loop through the gaussians
        for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){
        
            // Identify weights
            double *weights_ptr =       PyArray_GETPTR1(weights_arr, gauss_id);
        
            //// First loop; Identify maximum component ////
            // reset the maha distance
            double maha = 0;
            // Loop k
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                // reset r
                double r = 0;
                // loop l
                for (npy_intp dim2_id =0; dim2_id < ndim; dim2_id++) {
                    double *mu_ptr = PyArray_GETPTR2(mu_arr, gauss_id, dim2_id);
                    double *scale_ptr = PyArray_GETPTR2(scale_arr, gauss_id, dim2_id);
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim2_id, dim1_id);
                    double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim2_id);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            // Identify log pdf for this Gaussian component
            out_buffer = (-0.5 * (const_factor + log_det_cov + maha)) 
                + (*weights_ptr);
            // Check if this is a new maximum
            if ((sample_id == 0) | (out_buffer > (*out_ptr))) {
                *out_ptr = out_buffer;
            }

        }
        // Identify maximum of logpdf for this Gaussian component
        out_buffer = *out_ptr;
        // Reset output array
        *out_ptr = 0;
        // Loop through the gaussians
        for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){
            // Identify weights
            double *weights_ptr =       PyArray_GETPTR1(weights_arr, gauss_id);
            //// Calculate the mahalanobis distance ////
            // reset the maha distance
            double maha = 0;
            // Loop k
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                // reset r
                double r = 0;
                // loop l
                for (npy_intp dim2_id =0; dim2_id < ndim; dim2_id++) {
                    double *mu_ptr = PyArray_GETPTR2(mu_arr, gauss_id, dim2_id);
                    double *scale_ptr = PyArray_GETPTR2(scale_arr, gauss_id, dim2_id);
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim2_id, dim1_id);
                    double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim2_id);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            // Add in shifted exponential space
            *out_ptr += exp(((-0.5 * (const_factor + log_det_cov + maha)) 
                + (*weights_ptr)) - out_buffer);
        }
        // Shift output back
        *out_ptr *= exp(out_buffer);
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS

    // Free things
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (weights_arr)        {Py_DECREF(weights_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (limits_arr)         {Py_DECREF(limits_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (limits_arr)         {Py_DECREF(limits_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    if (out_obj)            {Py_DECREF(out_obj);}
    if (out_arr)            {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_gm_log_pdf_global_limits(PyObject *self, PyObject *args) {
    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // npts will describe the number of sample points
    npy_intp npts = 0;
    // ndim
    npy_intp ndim = 0;
    // keep
    npy_intp keep = 0;
    // factor for constatns
    double const_factor = 0;
    // determinant
    double log_det_cov = 0;
    // minimum eigenvalue
    double eps = 0;
    // Initialize output dimensions
    npy_intp eig_dims[3];
    npy_intp out_dims[1];

    // Py_objects for inputs and output objects
    PyObject *mu_obj = NULL;
    PyObject *scale_obj = NULL;
    PyObject *weights_obj = NULL;
    PyObject *eigvals_obj = NULL;
    PyObject *eigvecs_obj = NULL;
    PyObject *limits_obj = NULL;
    PyObject *sample_obj = NULL;
    PyObject *eigvecs_norm_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *mu_arr = NULL;
    PyArrayObject *scale_arr = NULL;
    PyArrayObject *weights_arr = NULL;
    PyArrayObject *eigvals_arr = NULL;
    PyArrayObject *eigvecs_arr = NULL;
    PyArrayObject *limits_arr = NULL;
    PyArrayObject *sample_arr = NULL;
    PyArrayObject *eigvecs_norm_arr = NULL;
    PyArrayObject *out_arr = NULL;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOOOOOd", &mu_obj, &scale_obj, &weights_obj, &eigvals_obj, &eigvecs_obj, &limits_obj, &sample_obj, &eps)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    // Check mu
    mu_arr = (PyArrayObject *)PyArray_FROM_O(mu_obj);
    check(mu_arr, "Failed to build mu_arr");
    check(PyArray_NDIM(mu_arr) == 2, "mu_arr should have 2 dimensions");

    // Check scale
    scale_arr = (PyArrayObject *)PyArray_FROM_O(scale_obj);
    check(scale_arr, "Failed to build scale_arr");
    check(PyArray_NDIM(scale_arr) == 2, "scale_arr should have 2 dimensions");

    // Check weights
    weights_arr = (PyArrayObject *)PyArray_FROM_O(weights_obj);
    check(weights_arr, "Failed to build weights_arr");
    check(PyArray_NDIM(weights_arr) == 1, "weights_arr should have 2 dimensions");

    // Check eigvals
    eigvals_arr = (PyArrayObject *)PyArray_FROM_O(eigvals_obj);
    check(eigvals_arr, "Failed to build eigvals_arr");
    check(PyArray_NDIM(eigvals_arr) == 2, "eigvals_arr should have 2 dimensions");

    // Check eigvecs
    eigvecs_arr = (PyArrayObject *)PyArray_FROM_O(eigvecs_obj);
    check(eigvecs_arr, "Failed to build eigvecs_arr");
    check(PyArray_NDIM(eigvecs_arr) == 3, "eigvecs_arr should have 2 dimensions");

    // Check limits
    limits_arr = (PyArrayObject *)PyArray_FROM_O(limits_obj);
    check(limits_arr, "Failed to build limits_arr");
    check(PyArray_NDIM(limits_arr) == 2, "limits_arr should have 2 dimensions");

    // Check sample
    sample_arr = (PyArrayObject *)PyArray_FROM_O(sample_obj);
    check(sample_arr, "Failed to build sample_arr");
    check(PyArray_NDIM(sample_arr) == 2, "sample_arr should have 2 dimensions");

    // Check dimensions
    ngauss = PyArray_DIM(mu_arr, 0);
    check(ngauss > 0, "ngauss should be greater than zero.");
    ndim = PyArray_DIM(mu_arr, 1);
    check(ndim > 0, "ndim should be greater than zero");
    npts = PyArray_DIM(sample_arr, 0);
    check(npts > 0, "npts should be greater than zero.");

    // Check scale
    check((PyArray_DIM(scale_arr, 0) == ngauss) & (PyArray_DIM(scale_arr, 1) == ndim),
        "Dimension mismatch between mu and scale.");
    // Check weights
    check((PyArray_DIM(weights_arr, 0) == ngauss),
        "Dimension mismatch between mu and weights.");
    // Check eigvals
    check((PyArray_DIM(eigvals_arr, 0) == ngauss) & (PyArray_DIM(eigvals_arr, 1) == ndim),
        "Dimension mismatch between mu and eigvals.");
    // Check eigvecs
    check(
          (PyArray_DIM(eigvecs_arr, 0) == ngauss) &
          (PyArray_DIM(eigvecs_arr, 1) == ndim) &
          (PyArray_DIM(eigvecs_arr, 2) == ndim),
          "Dimension mismatch between mu and eigvecs"
         );

    // Check limits
    check(
          (PyArray_DIM(limits_arr, 0) == ndim) &
          (PyArray_DIM(limits_arr, 1) == 2),
         );

    // Check sample
    check(PyArray_DIM(sample_arr, 1) == ndim,
        "Dimension mismatch between mu and sample.");


    // Build eigvecs_norm array
    // assign dims
    eig_dims[0] = ngauss;
    eig_dims[1] = ndim;
    eig_dims[2] = ndim;
    // make eigenvector norm object
    eigvecs_norm_obj = PyArray_ZEROS(3, eig_dims, NPY_DOUBLE, 0);
    check(eigvecs_norm_obj, "Failed to build eigvecs_norm_obj.");
    // Convert to array
    eigvecs_norm_arr = (PyArrayObject *) eigvecs_norm_obj;
    check(eigvecs_norm_arr, "Failed to build eigvecs_norm_arr.");
    // fill with zeroes
    PyArray_FILLWBYTE(eigvecs_norm_arr, 0);


    // Build output array
    // assign dims
    out_dims[0] = npts;
    // make out object
    out_obj = PyArray_ZEROS(1, out_dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    // Convert to array
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Assign constants
    const_factor = ((double)ndim) * log(2. * NPY_PI);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    // Loop through the gaussians
    for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){

        //// Calculate the log_det_cov ////
        // Initialize log_det_cov at 1
        log_det_cov = 1.;
        keep = 1;
        // Loop the dimensions
        for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
            // Find the eigenvalue pointer
            double *eigvals_ptr = PyArray_GETPTR2(eigvals_arr, gauss_id, dim1_id);
            // If the eigenvalue is greater than eps...
            if ((*eigvals_ptr) > eps) {
                // Then multiply its value into the determinant
                log_det_cov *= (*eigvals_ptr);
            // If not ... 
            } else {
                // singular matrix
                log_det_cov = 0;
                keep = 0;
            }
        }
        // Take the logarithm
        if (keep == 1) {
            log_det_cov = log(log_det_cov);
        }

        //// Calculate the orthonormalized eigenvectors ////
        // Only for non-singular eigenvalues:
        if (keep == 1) {
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                for (npy_intp dim2_id = 0; dim2_id < ndim; dim2_id++) {
                    // Find the eigenvalue pointer
                    double *eigvals_ptr = PyArray_GETPTR2(eigvals_arr, gauss_id, dim2_id);
                    // Find the eigenvector pointer
                    double *eigvecs_ptr = PyArray_GETPTR3(eigvecs_arr, gauss_id, dim1_id, dim2_id);
                    // Get the address of the vector
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim1_id, dim2_id);
                    // assign it a value
                    *eigvecs_norm_ptr =  (*eigvecs_ptr)/sqrt(*eigvals_ptr);
                }
            }
        }
    }
    // Close all threads; open new threads
    Py_END_ALLOW_THREADS
    Py_BEGIN_ALLOW_THREADS
    // Loop the output array
    #pragma omp parallel for
    for (npy_intp sample_id = 0; sample_id < npts; sample_id++){
        // find the out pointer
        double *out_ptr =              PyArray_GETPTR1(out_arr, sample_id);
        double out_buffer = 0;
        // Check global limits //
        npy_intp skip = 0;
        for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++){
            double *limits_lo_ptr = PyArray_GETPTR2(limits_arr, dim1_id, 0);
            double *limits_hi_ptr = PyArray_GETPTR2(limits_arr, dim1_id, 1);
            double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim1_id);
            if (
                (*sample_ptr < *limits_lo_ptr) | (*sample_ptr > *limits_hi_ptr)
            ) {
            skip += 1;
            }
        }
        // skip if not in limits //
        if (skip > 0) {
            *out_ptr = log(0);
            continue;
        }
        // Loop through the gaussians
        for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){
        
            // Identify weights
            double *weights_ptr =       PyArray_GETPTR1(weights_arr, gauss_id);
        
            //// First loop; Identify maximum component ////
            // reset the maha distance
            double maha = 0;
            // Loop k
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                // reset r
                double r = 0;
                // loop l
                for (npy_intp dim2_id =0; dim2_id < ndim; dim2_id++) {
                    double *mu_ptr = PyArray_GETPTR2(mu_arr, gauss_id, dim2_id);
                    double *scale_ptr = PyArray_GETPTR2(scale_arr, gauss_id, dim2_id);
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim2_id, dim1_id);
                    double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim2_id);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            // Identify log pdf for this Gaussian component
            out_buffer = (-0.5 * (const_factor + log_det_cov + maha)) 
                + (*weights_ptr);
            // Check if this is a new maximum
            if ((sample_id == 0) | (out_buffer > (*out_ptr))) {
                *out_ptr = out_buffer;
            }

        }
        // Identify maximum of logpdf for this Gaussian component
        out_buffer = *out_ptr;
        // Reset output array
        *out_ptr = 0;
        // Loop through the gaussians
        for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){
            // Identify weights
            double *weights_ptr =       PyArray_GETPTR1(weights_arr, gauss_id);
            //// Calculate the mahalanobis distance ////
            // reset the maha distance
            double maha = 0;
            // Loop k
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                // reset r
                double r = 0;
                // loop l
                for (npy_intp dim2_id =0; dim2_id < ndim; dim2_id++) {
                    double *mu_ptr = PyArray_GETPTR2(mu_arr, gauss_id, dim2_id);
                    double *scale_ptr = PyArray_GETPTR2(scale_arr, gauss_id, dim2_id);
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim2_id, dim1_id);
                    double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim2_id);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            // Add in shifted exponential space
            *out_ptr += exp(((-0.5 * (const_factor + log_det_cov + maha)) 
                + (*weights_ptr)) - out_buffer);
        }
        // Shift output back
        *out_ptr = log(*out_ptr) + out_buffer;
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS

    // Free things
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (weights_arr)        {Py_DECREF(weights_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (weights_arr)        {Py_DECREF(weights_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    if (out_obj)            {Py_DECREF(out_obj);}
    if (out_arr)            {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_gm_pdf_local_limits(PyObject *self, PyObject *args) {
    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // npts will describe the number of sample points
    npy_intp npts = 0;
    // ndim
    npy_intp ndim = 0;
    // keep
    npy_intp keep = 0;
    // factor for constatns
    double const_factor = 0;
    // determinant
    double log_det_cov = 0;
    // minimum eigenvalue
    double eps = 0;
    // Initialize output dimensions
    npy_intp eig_dims[3];
    npy_intp out_dims[1];

    // Py_objects for inputs and output objects
    PyObject *mu_obj = NULL;
    PyObject *scale_obj = NULL;
    PyObject *weights_obj = NULL;
    PyObject *eigvals_obj = NULL;
    PyObject *eigvecs_obj = NULL;
    PyObject *limits_obj = NULL;
    PyObject *sample_obj = NULL;
    PyObject *eigvecs_norm_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *mu_arr = NULL;
    PyArrayObject *scale_arr = NULL;
    PyArrayObject *weights_arr = NULL;
    PyArrayObject *eigvals_arr = NULL;
    PyArrayObject *eigvecs_arr = NULL;
    PyArrayObject *limits_arr = NULL;
    PyArrayObject *sample_arr = NULL;
    PyArrayObject *eigvecs_norm_arr = NULL;
    PyArrayObject *out_arr = NULL;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOOOOOd", &mu_obj, &scale_obj, &weights_obj, &eigvals_obj, &eigvecs_obj, &limits_obj, &sample_obj, &eps)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    // Check mu
    mu_arr = (PyArrayObject *)PyArray_FROM_O(mu_obj);
    check(mu_arr, "Failed to build mu_arr");
    check(PyArray_NDIM(mu_arr) == 2, "mu_arr should have 2 dimensions");

    // Check scale
    scale_arr = (PyArrayObject *)PyArray_FROM_O(scale_obj);
    check(scale_arr, "Failed to build scale_arr");
    check(PyArray_NDIM(scale_arr) == 2, "scale_arr should have 2 dimensions");

    // Check weights
    weights_arr = (PyArrayObject *)PyArray_FROM_O(weights_obj);
    check(weights_arr, "Failed to build weights_arr");
    check(PyArray_NDIM(weights_arr) == 1, "weights_arr should have 2 dimensions");

    // Check eigvals
    eigvals_arr = (PyArrayObject *)PyArray_FROM_O(eigvals_obj);
    check(eigvals_arr, "Failed to build eigvals_arr");
    check(PyArray_NDIM(eigvals_arr) == 2, "eigvals_arr should have 2 dimensions");

    // Check eigvecs
    eigvecs_arr = (PyArrayObject *)PyArray_FROM_O(eigvecs_obj);
    check(eigvecs_arr, "Failed to build eigvecs_arr");
    check(PyArray_NDIM(eigvecs_arr) == 3, "eigvecs_arr should have 2 dimensions");

    // Check limits
    limits_arr = (PyArrayObject *)PyArray_FROM_O(limits_obj);
    check(limits_arr, "Failed to build limits_arr");
    check(PyArray_NDIM(limits_arr) == 3, "limits_arr should have 3 dimensions");

    // Check sample
    sample_arr = (PyArrayObject *)PyArray_FROM_O(sample_obj);
    check(sample_arr, "Failed to build sample_arr");
    check(PyArray_NDIM(sample_arr) == 2, "sample_arr should have 2 dimensions");

    // Check dimensions
    ngauss = PyArray_DIM(mu_arr, 0);
    check(ngauss > 0, "ngauss should be greater than zero.");
    ndim = PyArray_DIM(mu_arr, 1);
    check(ndim > 0, "ndim should be greater than zero");
    npts = PyArray_DIM(sample_arr, 0);
    check(npts > 0, "npts should be greater than zero.");

    // Check scale
    check((PyArray_DIM(scale_arr, 0) == ngauss) & (PyArray_DIM(scale_arr, 1) == ndim),
        "Dimension mismatch between mu and scale.");
    // Check weights
    check((PyArray_DIM(weights_arr, 0) == ngauss),
        "Dimension mismatch between mu and weights.");
    // Check eigvals
    check((PyArray_DIM(eigvals_arr, 0) == ngauss) & (PyArray_DIM(eigvals_arr, 1) == ndim),
        "Dimension mismatch between mu and eigvals.");
    // Check eigvecs
    check(
          (PyArray_DIM(eigvecs_arr, 0) == ngauss) &
          (PyArray_DIM(eigvecs_arr, 1) == ndim) &
          (PyArray_DIM(eigvecs_arr, 2) == ndim),
          "Dimension mismatch between mu and eigvecs"
         );

    // Check limits
    check(
          (PyArray_DIM(limits_arr, 0) == ngauss) &
          (PyArray_DIM(limits_arr, 1) == ndim) &
          (PyArray_DIM(limits_arr, 2) == 2),
          "Dimension mismatch between mu and limits"
         );

    // Check sample
    check(PyArray_DIM(sample_arr, 1) == ndim,
        "Dimension mismatch between mu and sample.");


    // Build eigvecs_norm array
    // assign dims
    eig_dims[0] = ngauss;
    eig_dims[1] = ndim;
    eig_dims[2] = ndim;
    // make eigenvector norm object
    eigvecs_norm_obj = PyArray_ZEROS(3, eig_dims, NPY_DOUBLE, 0);
    check(eigvecs_norm_obj, "Failed to build eigvecs_norm_obj.");
    // Convert to array
    eigvecs_norm_arr = (PyArrayObject *) eigvecs_norm_obj;
    check(eigvecs_norm_arr, "Failed to build eigvecs_norm_arr.");
    // fill with zeroes
    PyArray_FILLWBYTE(eigvecs_norm_arr, 0);


    // Build output array
    // assign dims
    out_dims[0] = npts;
    // make out object
    out_obj = PyArray_ZEROS(1, out_dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    // Convert to array
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Assign constants
    const_factor = ((double)ndim) * log(2. * NPY_PI);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    // Loop through the gaussians
    for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){

        //// Calculate the log_det_cov ////
        // Initialize log_det_cov at 1
        log_det_cov = 1.;
        keep = 1;
        // Loop the dimensions
        for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
            // Find the eigenvalue pointer
            double *eigvals_ptr = PyArray_GETPTR2(eigvals_arr, gauss_id, dim1_id);
            // If the eigenvalue is greater than eps...
            if ((*eigvals_ptr) > eps) {
                // Then multiply its value into the determinant
                log_det_cov *= (*eigvals_ptr);
            // If not ... 
            } else {
                // singular matrix
                log_det_cov = 0;
                keep = 0;
            }
        }
        // Take the logarithm
        if (keep == 1) {
            log_det_cov = log(log_det_cov);
        }

        //// Calculate the orthonormalized eigenvectors ////
        // Only for non-singular eigenvalues:
        if (keep == 1) {
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                for (npy_intp dim2_id = 0; dim2_id < ndim; dim2_id++) {
                    // Find the eigenvalue pointer
                    double *eigvals_ptr = PyArray_GETPTR2(eigvals_arr, gauss_id, dim2_id);
                    // Find the eigenvector pointer
                    double *eigvecs_ptr = PyArray_GETPTR3(eigvecs_arr, gauss_id, dim1_id, dim2_id);
                    // Get the address of the vector
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim1_id, dim2_id);
                    // assign it a value
                    *eigvecs_norm_ptr =  (*eigvecs_ptr)/sqrt(*eigvals_ptr);
                }
            }
        }
    }
    // Close all threads; open new threads
    Py_END_ALLOW_THREADS
    Py_BEGIN_ALLOW_THREADS
    // Loop the output array
    #pragma omp parallel for
    for (npy_intp sample_id = 0; sample_id < npts; sample_id++){
        // find the out pointer
        double *out_ptr =              PyArray_GETPTR1(out_arr, sample_id);
        double out_buffer = 0;

        // Loop through the gaussians
        for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){
            // Check local limits //
            npy_intp skip = 0;
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++){
                double *limits_lo_ptr = 
                    PyArray_GETPTR3(limits_arr, gauss_id, dim1_id, 0);
                double *limits_hi_ptr = 
                    PyArray_GETPTR3(limits_arr, gauss_id, dim1_id, 1);
                double *sample_ptr = 
                    PyArray_GETPTR2(sample_arr, sample_id, dim1_id);
                if (
                    (*sample_ptr < *limits_lo_ptr) | (*sample_ptr > *limits_hi_ptr)
                ) {
                skip += 1;
                }
            }
            // skip if not in limits //
            if (skip > 0) {
                continue;
            }
            // Identify weights
            double *weights_ptr =       PyArray_GETPTR1(weights_arr, gauss_id);
        
            //// First loop; Identify maximum component ////
            // reset the maha distance
            double maha = 0;
            // Loop k
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                // reset r
                double r = 0;
                // loop l
                for (npy_intp dim2_id =0; dim2_id < ndim; dim2_id++) {
                    double *mu_ptr = PyArray_GETPTR2(mu_arr, gauss_id, dim2_id);
                    double *scale_ptr = PyArray_GETPTR2(scale_arr, gauss_id, dim2_id);
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim2_id, dim1_id);
                    double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim2_id);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            // Identify log pdf for this Gaussian component
            out_buffer = (-0.5 * (const_factor + log_det_cov + maha)) 
                + (*weights_ptr);
            // Check if this is a new maximum
            if ((sample_id == 0) | (out_buffer > (*out_ptr))) {
                *out_ptr = out_buffer;
            }

        }
        // Identify maximum of logpdf for this Gaussian component
        out_buffer = *out_ptr;
        // Reset output array
        *out_ptr = 0;
        // Loop through the gaussians
        for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){
            // Check local limits //
            npy_intp skip = 0;
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++){
                double *limits_lo_ptr = 
                    PyArray_GETPTR3(limits_arr, gauss_id, dim1_id, 0);
                double *limits_hi_ptr = 
                    PyArray_GETPTR3(limits_arr, gauss_id, dim1_id, 1);
                double *sample_ptr = 
                    PyArray_GETPTR2(sample_arr, sample_id, dim1_id);
                if (
                    (*sample_ptr < *limits_lo_ptr) | (*sample_ptr > *limits_hi_ptr)
                ) {
                skip += 1;
                }
            }
            // skip if not in limits //
            if (skip > 0) {
                continue;
            }
            // Identify weights
            double *weights_ptr =       PyArray_GETPTR1(weights_arr, gauss_id);
            //// Calculate the mahalanobis distance ////
            // reset the maha distance
            double maha = 0;
            // Loop k
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                // reset r
                double r = 0;
                // loop l
                for (npy_intp dim2_id =0; dim2_id < ndim; dim2_id++) {
                    double *mu_ptr = PyArray_GETPTR2(mu_arr, gauss_id, dim2_id);
                    double *scale_ptr = PyArray_GETPTR2(scale_arr, gauss_id, dim2_id);
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim2_id, dim1_id);
                    double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim2_id);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            // Add in shifted exponential space
            *out_ptr += exp(((-0.5 * (const_factor + log_det_cov + maha)) 
                + (*weights_ptr)) - out_buffer);
        }
        // Shift output back
        *out_ptr *= exp(out_buffer);
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS

    // Free things
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (weights_arr)        {Py_DECREF(weights_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (limits_arr)         {Py_DECREF(limits_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (limits_arr)         {Py_DECREF(limits_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    if (out_obj)            {Py_DECREF(out_obj);}
    if (out_arr)            {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

static PyObject *_gm_log_pdf_local_limits(PyObject *self, PyObject *args) {
    // ngauss will describe the number of gaussians (points of the first set)
    npy_intp ngauss = 0;
    // npts will describe the number of sample points
    npy_intp npts = 0;
    // ndim
    npy_intp ndim = 0;
    // keep
    npy_intp keep = 0;
    // factor for constatns
    double const_factor = 0;
    // determinant
    double log_det_cov = 0;
    // minimum eigenvalue
    double eps = 0;
    // Initialize output dimensions
    npy_intp eig_dims[3];
    npy_intp out_dims[1];

    // Py_objects for inputs and output objects
    PyObject *mu_obj = NULL;
    PyObject *scale_obj = NULL;
    PyObject *weights_obj = NULL;
    PyObject *eigvals_obj = NULL;
    PyObject *eigvecs_obj = NULL;
    PyObject *limits_obj = NULL;
    PyObject *sample_obj = NULL;
    PyObject *eigvecs_norm_obj = NULL;
    PyObject *out_obj = NULL;
    // PyArray objects for array data
    PyArrayObject *mu_arr = NULL;
    PyArrayObject *scale_arr = NULL;
    PyArrayObject *weights_arr = NULL;
    PyArrayObject *eigvals_arr = NULL;
    PyArrayObject *eigvecs_arr = NULL;
    PyArrayObject *limits_arr = NULL;
    PyArrayObject *sample_arr = NULL;
    PyArrayObject *eigvecs_norm_arr = NULL;
    PyArrayObject *out_arr = NULL;

    // Parse the argument tuple
    if (!PyArg_ParseTuple(args, "OOOOOOOd", &mu_obj, &scale_obj, &weights_obj, &eigvals_obj, &eigvecs_obj, &limits_obj, &sample_obj, &eps)) {
        PyErr_SetString(PyExc_TypeError, "Error parsing input");
        return NULL;
    }

    // Fill the array pointers
    // Check mu
    mu_arr = (PyArrayObject *)PyArray_FROM_O(mu_obj);
    check(mu_arr, "Failed to build mu_arr");
    check(PyArray_NDIM(mu_arr) == 2, "mu_arr should have 2 dimensions");

    // Check scale
    scale_arr = (PyArrayObject *)PyArray_FROM_O(scale_obj);
    check(scale_arr, "Failed to build scale_arr");
    check(PyArray_NDIM(scale_arr) == 2, "scale_arr should have 2 dimensions");

    // Check weights
    weights_arr = (PyArrayObject *)PyArray_FROM_O(weights_obj);
    check(weights_arr, "Failed to build weights_arr");
    check(PyArray_NDIM(weights_arr) == 1, "weights_arr should have 2 dimensions");

    // Check eigvals
    eigvals_arr = (PyArrayObject *)PyArray_FROM_O(eigvals_obj);
    check(eigvals_arr, "Failed to build eigvals_arr");
    check(PyArray_NDIM(eigvals_arr) == 2, "eigvals_arr should have 2 dimensions");

    // Check eigvecs
    eigvecs_arr = (PyArrayObject *)PyArray_FROM_O(eigvecs_obj);
    check(eigvecs_arr, "Failed to build eigvecs_arr");
    check(PyArray_NDIM(eigvecs_arr) == 3, "eigvecs_arr should have 2 dimensions");

    // Check limits
    limits_arr = (PyArrayObject *)PyArray_FROM_O(limits_obj);
    check(limits_arr, "Failed to build limits_arr");
    check(PyArray_NDIM(limits_arr) == 3, "limits_arr should have 3 dimensions");

    // Check sample
    sample_arr = (PyArrayObject *)PyArray_FROM_O(sample_obj);
    check(sample_arr, "Failed to build sample_arr");
    check(PyArray_NDIM(sample_arr) == 2, "sample_arr should have 2 dimensions");

    // Check dimensions
    ngauss = PyArray_DIM(mu_arr, 0);
    check(ngauss > 0, "ngauss should be greater than zero.");
    ndim = PyArray_DIM(mu_arr, 1);
    check(ndim > 0, "ndim should be greater than zero");
    npts = PyArray_DIM(sample_arr, 0);
    check(npts > 0, "npts should be greater than zero.");

    // Check scale
    check((PyArray_DIM(scale_arr, 0) == ngauss) & (PyArray_DIM(scale_arr, 1) == ndim),
        "Dimension mismatch between mu and scale.");
    // Check weights
    check((PyArray_DIM(weights_arr, 0) == ngauss),
        "Dimension mismatch between mu and weights.");
    // Check eigvals
    check((PyArray_DIM(eigvals_arr, 0) == ngauss) & (PyArray_DIM(eigvals_arr, 1) == ndim),
        "Dimension mismatch between mu and eigvals.");
    // Check eigvecs
    check(
          (PyArray_DIM(eigvecs_arr, 0) == ngauss) &
          (PyArray_DIM(eigvecs_arr, 1) == ndim) &
          (PyArray_DIM(eigvecs_arr, 2) == ndim),
          "Dimension mismatch between mu and eigvecs"
         );

    // Check limits
    check(
          (PyArray_DIM(limits_arr, 0) == ngauss) &
          (PyArray_DIM(limits_arr, 1) == ndim) &
          (PyArray_DIM(limits_arr, 2) == 2),
          "Dimension mismatch between mu and limits"
         );

    // Check sample
    check(PyArray_DIM(sample_arr, 1) == ndim,
        "Dimension mismatch between mu and sample.");


    // Build eigvecs_norm array
    // assign dims
    eig_dims[0] = ngauss;
    eig_dims[1] = ndim;
    eig_dims[2] = ndim;
    // make eigenvector norm object
    eigvecs_norm_obj = PyArray_ZEROS(3, eig_dims, NPY_DOUBLE, 0);
    check(eigvecs_norm_obj, "Failed to build eigvecs_norm_obj.");
    // Convert to array
    eigvecs_norm_arr = (PyArrayObject *) eigvecs_norm_obj;
    check(eigvecs_norm_arr, "Failed to build eigvecs_norm_arr.");
    // fill with zeroes
    PyArray_FILLWBYTE(eigvecs_norm_arr, 0);


    // Build output array
    // assign dims
    out_dims[0] = npts;
    // make out object
    out_obj = PyArray_ZEROS(1, out_dims, NPY_DOUBLE, 0);
    check(out_obj, "Failed to build output object.");
    // Convert to array
    out_arr = (PyArrayObject *)out_obj;
    check(out_arr, "Failed to build output array.");
    // Fill out with zeros
    PyArray_FILLWBYTE(out_arr, 0);

    // Assign constants
    const_factor = ((double)ndim) * log(2. * NPY_PI);

    // Allow multithreading
    Py_BEGIN_ALLOW_THREADS
    // Loop through the gaussians
    for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){

        //// Calculate the log_det_cov ////
        // Initialize log_det_cov at 1
        log_det_cov = 1.;
        keep = 1;
        // Loop the dimensions
        for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
            // Find the eigenvalue pointer
            double *eigvals_ptr = PyArray_GETPTR2(eigvals_arr, gauss_id, dim1_id);
            // If the eigenvalue is greater than eps...
            if ((*eigvals_ptr) > eps) {
                // Then multiply its value into the determinant
                log_det_cov *= (*eigvals_ptr);
            // If not ... 
            } else {
                // singular matrix
                log_det_cov = 0;
                keep = 0;
            }
        }
        // Take the logarithm
        if (keep == 1) {
            log_det_cov = log(log_det_cov);
        }

        //// Calculate the orthonormalized eigenvectors ////
        // Only for non-singular eigenvalues:
        if (keep == 1) {
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                for (npy_intp dim2_id = 0; dim2_id < ndim; dim2_id++) {
                    // Find the eigenvalue pointer
                    double *eigvals_ptr = PyArray_GETPTR2(eigvals_arr, gauss_id, dim2_id);
                    // Find the eigenvector pointer
                    double *eigvecs_ptr = PyArray_GETPTR3(eigvecs_arr, gauss_id, dim1_id, dim2_id);
                    // Get the address of the vector
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim1_id, dim2_id);
                    // assign it a value
                    *eigvecs_norm_ptr =  (*eigvecs_ptr)/sqrt(*eigvals_ptr);
                }
            }
        }
    }
    // Close all threads; open new threads
    Py_END_ALLOW_THREADS
    Py_BEGIN_ALLOW_THREADS
    // Loop the output array
    #pragma omp parallel for
    for (npy_intp sample_id = 0; sample_id < npts; sample_id++){
        // find the out pointer
        double *out_ptr =              PyArray_GETPTR1(out_arr, sample_id);
        double out_buffer = 0;

        // Loop through the gaussians
        for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){
            // Check local limits //
            npy_intp skip = 0;
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++){
                double *limits_lo_ptr = 
                    PyArray_GETPTR3(limits_arr, gauss_id, dim1_id, 0);
                double *limits_hi_ptr = 
                    PyArray_GETPTR3(limits_arr, gauss_id, dim1_id, 1);
                double *sample_ptr = 
                    PyArray_GETPTR2(sample_arr, sample_id, dim1_id);
                if (
                    (*sample_ptr < *limits_lo_ptr) | (*sample_ptr > *limits_hi_ptr)
                ) {
                skip += 1;
                }
            }
            // skip if not in limits //
            if (skip > 0) {
                continue;
            }
            // Identify weights
            double *weights_ptr =       PyArray_GETPTR1(weights_arr, gauss_id);
        
            //// First loop; Identify maximum component ////
            // reset the maha distance
            double maha = 0;
            // Loop k
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                // reset r
                double r = 0;
                // loop l
                for (npy_intp dim2_id =0; dim2_id < ndim; dim2_id++) {
                    double *mu_ptr = PyArray_GETPTR2(mu_arr, gauss_id, dim2_id);
                    double *scale_ptr = PyArray_GETPTR2(scale_arr, gauss_id, dim2_id);
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim2_id, dim1_id);
                    double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim2_id);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            // Identify log pdf for this Gaussian component
            out_buffer = (-0.5 * (const_factor + log_det_cov + maha)) 
                + (*weights_ptr);
            // Check if this is a new maximum
            if ((sample_id == 0) | (out_buffer > (*out_ptr))) {
                *out_ptr = out_buffer;
            }

        }
        // Identify maximum of logpdf for this Gaussian component
        out_buffer = *out_ptr;
        // Reset output array
        *out_ptr = 0;
        // Loop through the gaussians
        for (npy_intp gauss_id = 0; gauss_id < ngauss; gauss_id++){
            // Check local limits //
            npy_intp skip = 0;
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++){
                double *limits_lo_ptr = 
                    PyArray_GETPTR3(limits_arr, gauss_id, dim1_id, 0);
                double *limits_hi_ptr = 
                    PyArray_GETPTR3(limits_arr, gauss_id, dim1_id, 1);
                double *sample_ptr = 
                    PyArray_GETPTR2(sample_arr, sample_id, dim1_id);
                if (
                    (*sample_ptr < *limits_lo_ptr) | (*sample_ptr > *limits_hi_ptr)
                ) {
                skip += 1;
                }
            }
            // skip if not in limits //
            if (skip > 0) {
                continue;
            }
            // Identify weights
            double *weights_ptr =       PyArray_GETPTR1(weights_arr, gauss_id);
            //// Calculate the mahalanobis distance ////
            // reset the maha distance
            double maha = 0;
            // Loop k
            for (npy_intp dim1_id = 0; dim1_id < ndim; dim1_id++) {
                // reset r
                double r = 0;
                // loop l
                for (npy_intp dim2_id =0; dim2_id < ndim; dim2_id++) {
                    double *mu_ptr = PyArray_GETPTR2(mu_arr, gauss_id, dim2_id);
                    double *scale_ptr = PyArray_GETPTR2(scale_arr, gauss_id, dim2_id);
                    double *eigvecs_norm_ptr = PyArray_GETPTR3(eigvecs_norm_arr, gauss_id, dim2_id, dim1_id);
                    double *sample_ptr = PyArray_GETPTR2(sample_arr, sample_id, dim2_id);
                    r += (*eigvecs_norm_ptr) * (*sample_ptr - *mu_ptr) * (*scale_ptr);
                }
                // Add to maha
                maha += pow(r,2);
            }
            // Add in shifted exponential space
            *out_ptr += exp(((-0.5 * (const_factor + log_det_cov + maha)) 
                + (*weights_ptr)) - out_buffer);
        }
        // Shift output back
        *out_ptr = log(*out_ptr) + out_buffer;
    }
    // Cut out the multithreading nonsense
    Py_END_ALLOW_THREADS

    // Free things
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (weights_arr)        {Py_DECREF(weights_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    // Return output array
    return out_obj;

// Error
error:
    if (mu_arr)             {Py_DECREF(mu_arr);}
    if (scale_arr)          {Py_DECREF(scale_arr);}
    if (weights_arr)        {Py_DECREF(weights_arr);}
    if (eigvals_arr)        {Py_DECREF(eigvals_arr);}
    if (eigvecs_arr)        {Py_DECREF(eigvecs_arr);}
    if (sample_arr)         {Py_DECREF(sample_arr);}
    if (eigvecs_norm_arr)   {Py_DECREF(eigvecs_norm_arr);}
    if (out_obj)            {Py_DECREF(out_obj);}
    if (out_arr)            {Py_DECREF(out_arr);}
    PyErr_SetString(PyExc_RuntimeError, "C error");
    return NULL;
}

